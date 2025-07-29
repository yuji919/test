import os
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from PIL import Image
import io

from app.models import models
from app.schemas import schemas

class PhotoService:
    """사진 업로드 서비스"""
    
    def __init__(self):
        # 업로드 디렉토리 설정
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # 허용된 이미지 타입
        self.allowed_types = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp"
        }
        
        # 최대 파일 크기 (10MB)
        self.max_file_size = 10 * 1024 * 1024
    
    def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """파일 유효성 검사"""
        # 파일 크기 확인
        if file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"파일 크기가 너무 큽니다. 최대 {self.max_file_size // (1024*1024)}MB까지 허용됩니다."
            )
        
        # 파일 타입 확인
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 파일 타입입니다. 지원 타입: {', '.join(self.allowed_types.keys())}"
            )
        
        return {
            "content_type": file.content_type,
            "extension": self.allowed_types[file.content_type]
        }
    
    def save_file(self, file: UploadFile, user_id: int) -> Dict[str, Any]:
        """파일 저장"""
        # 파일 유효성 검사
        file_info = self.validate_file(file)
        
        # 고유한 파일명 생성
        unique_filename = f"{uuid.uuid4()}{file_info['extension']}"
        
        # 사용자별 디렉토리 생성
        user_upload_dir = self.upload_dir / str(user_id)
        user_upload_dir.mkdir(exist_ok=True)
        
        # 파일 경로
        file_path = user_upload_dir / unique_filename
        
        # 파일 저장
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"파일 저장 중 오류가 발생했습니다: {str(e)}")
        
        # 이미지 메타데이터 추출
        metadata = self.extract_image_metadata(file_path)
        
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "content_type": file_info["content_type"],
            "metadata": metadata
        }
    
    def extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """이미지 메타데이터 추출"""
        try:
            with Image.open(file_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                }
        except Exception:
            return {}
    
    def upload_photo(self, db: Session, user_id: int, file: UploadFile, 
                    photo_data: schemas.PhotoUploadRequest) -> Dict[str, Any]:
        """사진 업로드"""
        try:
            # 사용자 존재 확인
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
            
            # 파일 저장
            file_info = self.save_file(file, user_id)
            
            # 대표 사진으로 설정하는 경우, 기존 대표 사진 해제
            if photo_data.is_primary:
                existing_primary = db.query(models.Photo).filter(
                    models.Photo.user_id == user_id,
                    models.Photo.is_primary == True,
                    models.Photo.is_active == True
                ).first()
                if existing_primary:
                    existing_primary.is_primary = False
            
            # 데이터베이스에 사진 정보 저장
            photo = models.Photo(
                user_id=user_id,
                filename=file_info["filename"],
                original_filename=file_info["original_filename"],
                file_path=file_info["file_path"],
                file_size=file_info["file_size"],
                image_type=photo_data.image_type,
                description=photo_data.description,
                is_primary=photo_data.is_primary,
                width=file_info["metadata"].get("width"),
                height=file_info["metadata"].get("height"),
                mime_type=file_info["content_type"]
            )
            
            db.add(photo)
            db.commit()
            db.refresh(photo)
            
            return {
                "photo_id": photo.id,
                "filename": photo.filename,
                "file_path": photo.file_path,
                "file_size": photo.file_size,
                "message": "사진이 성공적으로 업로드되었습니다."
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"사진 업로드 중 오류가 발생했습니다: {str(e)}")
    
    def get_user_photos(self, db: Session, user_id: int) -> List[models.Photo]:
        """사용자의 사진 목록 조회"""
        photos = db.query(models.Photo).filter(
            models.Photo.user_id == user_id,
            models.Photo.is_active == True
        ).order_by(models.Photo.is_primary.desc(), models.Photo.created_at.desc()).all()
        
        return photos
    
    def get_photo(self, db: Session, photo_id: int) -> Optional[models.Photo]:
        """사진 상세 조회"""
        return db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    
    def update_photo(self, db: Session, photo_id: int, photo_data: schemas.PhotoUpdate) -> Dict[str, Any]:
        """사진 정보 수정"""
        photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
        if not photo:
            raise HTTPException(status_code=404, detail="사진을 찾을 수 없습니다")
        
        # 대표 사진으로 설정하는 경우, 기존 대표 사진 해제
        if photo_data.is_primary and not photo.is_primary:
            existing_primary = db.query(models.Photo).filter(
                models.Photo.user_id == photo.user_id,
                models.Photo.is_primary == True,
                models.Photo.is_active == True,
                models.Photo.id != photo_id
            ).first()
            if existing_primary:
                existing_primary.is_primary = False
        
        # 정보 업데이트
        for key, value in photo_data.dict(exclude_unset=True).items():
            setattr(photo, key, value)
        
        db.commit()
        db.refresh(photo)
        
        return {
            "photo_id": photo.id,
            "message": "사진 정보가 성공적으로 수정되었습니다."
        }
    
    def delete_photo(self, db: Session, photo_id: int) -> Dict[str, Any]:
        """사진 삭제 (소프트 삭제)"""
        photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
        if not photo:
            raise HTTPException(status_code=404, detail="사진을 찾을 수 없습니다")
        
        # 파일 삭제
        try:
            file_path = Path(photo.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"파일 삭제 중 오류: {str(e)}")
        
        # 데이터베이스에서 삭제
        db.delete(photo)
        db.commit()
        
        return {
            "message": "사진이 성공적으로 삭제되었습니다."
        }
    
    def get_photo_url(self, photo: models.Photo) -> str:
        """사진 URL 생성"""
        return f"/photos/{photo.user_id}/{photo.filename}" 