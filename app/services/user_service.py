from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
from typing import Dict, Any, Optional
from datetime import datetime

class UserService:
    """간단한 내정보 등록 서비스"""
    
    def __init__(self):
        pass
    
    def create_user_info(self, db: Session, user_info: schemas.UserCreate) -> Dict[str, Any]:
        """내정보 등록 (성명, 연락처, 나이, 성별, 실종 위치 - 필수)"""
        try:
            db_user = models.User(**user_info.dict())
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return {
                "user_id": db_user.id,
                "step": "complete",
                "is_complete": True,
                "message": "내정보가 성공적으로 등록되었습니다."
            }
        except Exception as e:
            db.rollback()
            return {
                "error": f"내정보 등록 중 오류가 발생했습니다: {str(e)}"
            }
    
    def get_user_info(self, db: Session, user_id: int) -> Dict[str, Any]:
        """내정보 조회"""
        try:
            db_user = db.query(models.User).filter(models.User.id == user_id).first()
            if not db_user:
                return {"error": "사용자를 찾을 수 없습니다."}
            
            return {
                "user_id": db_user.id,
                "name": db_user.name,
                "phone": db_user.phone,
                "age": db_user.age,
                "gender": db_user.gender,
                "missing_location": db_user.missing_location,
                "created_at": db_user.created_at,
                "message": "내정보를 성공적으로 조회했습니다."
            }
        except Exception as e:
            return {
                "error": f"내정보 조회 중 오류가 발생했습니다: {str(e)}"
            }
    
    def update_user_info(self, db: Session, user_id: int, user_info: schemas.UserUpdate) -> Dict[str, Any]:
        """내정보 수정"""
        try:
            db_user = db.query(models.User).filter(models.User.id == user_id).first()
            if not db_user:
                return {"error": "사용자를 찾을 수 없습니다."}
            
            # 내정보 업데이트
            for field, value in user_info.dict(exclude_unset=True).items():
                setattr(db_user, field, value)
            
            db.commit()
            db.refresh(db_user)
            
            return {
                "user_id": db_user.id,
                "message": "내정보가 성공적으로 수정되었습니다."
            }
        except Exception as e:
            db.rollback()
            return {
                "error": f"내정보 수정 중 오류가 발생했습니다: {str(e)}"
            } 