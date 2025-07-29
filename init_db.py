from app.database.database import engine
from app.models.models import Base, User, FrequentPlace, MissingChild, Hotzone, Notice, EmergencyContact

def init_database():
    """데이터베이스 테이블 생성"""
    print("데이터베이스 테이블을 생성합니다...")
    Base.metadata.create_all(bind=engine)
    print("데이터베이스 테이블 생성 완료!")

def insert_sample_data():
    """샘플 데이터 삽입"""
    from app.database.database import SessionLocal
    from datetime import datetime
    
    db = SessionLocal()
    
    try:
        # 긴급 연락처 샘플 데이터
        emergency_contacts = [
            EmergencyContact(
                name="112 긴급신고센터",
                phone_number="112",
                description="긴급신고 전화번호",
                contact_type="emergency"
            ),
            EmergencyContact(
                name="182 실종아동센터",
                phone_number="182",
                description="실종아동 전문 상담",
                contact_type="center"
            )
        ]
        
        for contact in emergency_contacts:
            db.add(contact)
        
        # 공지사항 샘플 데이터
        notices = [
            Notice(
                title="실종아동 찾기 앱 사용 안내",
                content="실종아동 찾기 앱을 통해 더 빠르고 정확한 실종아동 찾기가 가능합니다.",
                notice_type="guide",
                priority=1
            ),
            Notice(
                title="핫존 기능 업데이트",
                content="나이대별 맞춤 핫존 생성 기능이 추가되었습니다.",
                notice_type="update",
                priority=2
            )
        ]
        
        for notice in notices:
            db.add(notice)
        
        db.commit()
        print("샘플 데이터 삽입 완료!")
        
    except Exception as e:
        print(f"샘플 데이터 삽입 중 오류: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    insert_sample_data()
