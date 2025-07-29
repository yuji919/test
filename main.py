from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.database import get_db, engine
from app.models import models
from app.schemas import schemas
from app.services.hotzone_service import HotzoneService
from app.services.user_service import UserService
from app.services.photo_service import PhotoService
from typing import List
import uvicorn
from pathlib import Path
import shutil
from starlette.responses import FileResponse

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="실종아동 찾기 백엔드 API",
    description="실종아동 찾기를 위한 핫존 생성 및 관리 API",
    version="1.0.0"
)

# 서비스 인스턴스
hotzone_service = HotzoneService()
user_service = UserService()
photo_service = PhotoService()

@app.get("/")
def read_root():
    return {"message": "실종아동 찾기 백엔드 API"}

# ===== 사진 업로드 API =====

@app.post("/photos/upload/{user_id}", response_model=schemas.PhotoUploadResponse)
async def upload_photo(
    user_id: int,
    file: UploadFile = File(...),
    image_type: str = Form(...),
    description: str = Form(None),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db)
):
    """사진 업로드"""
    photo_data = schemas.PhotoUploadRequest(
        image_type=image_type,
        description=description,
        is_primary=is_primary
    )
    
    result = photo_service.upload_photo(db, user_id, file, photo_data)
    return result

@app.get("/photos/user/{user_id}", response_model=List[schemas.Photo])
def get_user_photos(user_id: int, db: Session = Depends(get_db)):
    """사용자의 사진 목록 조회"""
    photos = photo_service.get_user_photos(db, user_id)
    return photos

@app.get("/photos/{photo_id}", response_model=schemas.Photo)
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """사진 상세 조회"""
    photo = photo_service.get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="사진을 찾을 수 없습니다")
    return photo

@app.put("/photos/{photo_id}")
def update_photo(
    photo_id: int,
    photo_data: schemas.PhotoUpdate,
    db: Session = Depends(get_db)
):
    """사진 정보 수정"""
    result = photo_service.update_photo(db, photo_id, photo_data)
    return result

@app.delete("/photos/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """사진 삭제"""
    result = photo_service.delete_photo(db, photo_id)
    return result

@app.get("/photos/{user_id}/{filename}")
async def serve_photo(user_id: int, filename: str):
    """사진 파일 서빙"""
    file_path = Path(f"uploads/{user_id}/{filename}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    return FileResponse(file_path)

# ===== 간단한 내정보 등록 API =====

@app.post("/user-info/", response_model=schemas.UserInfoResponse)
def create_user_info(user_info: schemas.UserCreate, db: Session = Depends(get_db)):
    """내정보 등록 (성명, 연락처, 나이, 성별, 실종 위치 - 필수)"""
    result = user_service.create_user_info(db, user_info)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/user-info/{user_id}")
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    """내정보 조회"""
    result = user_service.get_user_info(db, user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.put("/user-info/{user_id}")
def update_user_info(user_id: int, user_info: schemas.UserUpdate, db: Session = Depends(get_db)):
    """내정보 수정"""
    result = user_service.update_user_info(db, user_id, user_info)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# ===== 기존 API들 =====

# 사용자 관련 API
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """사용자 정보 생성"""
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 정보 조회"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """사용자 정보 수정"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# 자주 가는 곳 관련 API
@app.post("/frequent-places/", response_model=schemas.FrequentPlace)
def create_frequent_places(frequent_place: schemas.FrequentPlaceCreate, db: Session = Depends(get_db)):
    """자주 가는 곳 정보 생성"""
    db_frequent_place = models.FrequentPlace(**frequent_place.dict())
    db.add(db_frequent_place)
    db.commit()
    db.refresh(db_frequent_place)
    return db_frequent_place

@app.get("/frequent-places/{user_id}", response_model=schemas.FrequentPlace)
def get_frequent_places(user_id: int, db: Session = Depends(get_db)):
    """사용자의 자주 가는 곳 정보 조회"""
    frequent_place = db.query(models.FrequentPlace).filter(models.FrequentPlace.user_id == user_id).first()
    if not frequent_place:
        raise HTTPException(status_code=404, detail="자주 가는 곳 정보를 찾을 수 없습니다")
    return frequent_place

# 핫존 관련 API
@app.post("/hotzones/create/")
def create_hotzones(request: schemas.HotzoneRequest):
    """핫존 생성"""
    result = hotzone_service.create_hotzones(
        user_id=request.user_id,
        missing_location=request.missing_location,
        child_age=request.child_age,
        radius_km=request.radius_km
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.get("/hotzones/{missing_child_id}", response_model=List[schemas.Hotzone])
def get_hotzones(missing_child_id: int, db: Session = Depends(get_db)):
    """실종아동의 핫존 목록 조회"""
    hotzones = db.query(models.Hotzone).filter(models.Hotzone.missing_child_id == missing_child_id).all()
    return hotzones

# 공지사항 관련 API
@app.get("/notices/", response_model=List[schemas.Notice])
def get_notices(db: Session = Depends(get_db)):
    """공지사항 목록 조회"""
    notices = db.query(models.Notice).filter(models.Notice.is_active == True).all()
    return notices

@app.get("/notices/{notice_id}", response_model=schemas.Notice)
def get_notice(notice_id: int, db: Session = Depends(get_db)):
    """공지사항 상세 조회"""
    notice = db.query(models.Notice).filter(models.Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
    return notice

# 긴급 연락처 관련 API
@app.get("/emergency-contacts/", response_model=List[schemas.EmergencyContact])
def get_emergency_contacts(db: Session = Depends(get_db)):
    """긴급 연락처 목록 조회"""
    contacts = db.query(models.EmergencyContact).filter(models.EmergencyContact.is_active == True).all()
    return contacts

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
