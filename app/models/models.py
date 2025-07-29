from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class User(Base):
    """사용자 정보 테이블 (보호자 정보)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    guardian_name = Column(String(100), nullable=False, comment="보호자 성명")
    guardian_phone = Column(String(20), nullable=False, comment="보호자 연락처")
    child_name = Column(String(100), nullable=False, comment="아이 이름")
    child_gender = Column(String(10), nullable=False, comment="아이 성별 (남/여)")
    child_birth_date = Column(String(20), nullable=False, comment="아이 생년월일")
    child_characteristics = Column(Text, comment="아이 특징")
    child_height = Column(Float, comment="아이 키 (cm)")
    child_weight = Column(Float, comment="아이 몸무게 (kg)")
    child_clothing = Column(Text, comment="아이 옷차림")
    
    # 자주 가는 곳들 (1:1 관계)
    frequent_places = relationship("FrequentPlace", back_populates="user")
    
    # 실종아동 정보 (1:1 관계)
    missing_child = relationship("MissingChild", back_populates="user")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class FrequentPlace(Base):
    """자주 가는 곳 정보 테이블"""
    __tablename__ = "frequent_places"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    place1_name = Column(String(200), comment="자주 가는 곳 1")
    place1_address = Column(String(500), comment="자주 가는 곳 1 주소")
    place1_latitude = Column(Float, comment="자주 가는 곳 1 위도")
    place1_longitude = Column(Float, comment="자주 가는 곳 1 경도")
    
    place2_name = Column(String(200), comment="자주 가는 곳 2")
    place2_address = Column(String(500), comment="자주 가는 곳 2 주소")
    place2_latitude = Column(Float, comment="자주 가는 곳 2 위도")
    place2_longitude = Column(Float, comment="자주 가는 곳 2 경도")
    
    place3_name = Column(String(200), comment="자주 가는 곳 3")
    place3_address = Column(String(500), comment="자주 가는 곳 3 주소")
    place3_latitude = Column(Float, comment="자주 가는 곳 3 위도")
    place3_longitude = Column(Float, comment="자주 가는 곳 3 경도")
    
    place4_name = Column(String(200), comment="자주 가는 곳 4")
    place4_address = Column(String(500), comment="자주 가는 곳 4 주소")
    place4_latitude = Column(Float, comment="자주 가는 곳 4 위도")
    place4_longitude = Column(Float, comment="자주 가는 곳 4 경도")
    
    # User와의 관계
    user = relationship("User", back_populates="frequent_places")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MissingChild(Base):
    """실종아동 정보 테이블"""
    __tablename__ = "missing_children"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    missing_date = Column(DateTime, nullable=False, comment="실종 날짜")
    missing_location = Column(String(500), nullable=False, comment="실종 위치")
    missing_latitude = Column(Float, comment="실종 위치 위도")
    missing_longitude = Column(Float, comment="실종 위치 경도")
    
    child_age = Column(Integer, nullable=False, comment="실종 당시 나이")
    child_description = Column(Text, comment="추가 설명")
    
    # 실종 상태
    status = Column(String(20), default="missing", comment="상태 (missing/found)")
    
    # User와의 관계
    user = relationship("User", back_populates="missing_child")
    
    # 핫존 정보와의 관계
    hotzones = relationship("Hotzone", back_populates="missing_child")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Hotzone(Base):
    """핫존 정보 테이블"""
    __tablename__ = "hotzones"
    
    id = Column(Integer, primary_key=True, index=True)
    missing_child_id = Column(Integer, ForeignKey("missing_children.id"), nullable=False)
    
    place_name = Column(String(200), nullable=False, comment="장소명")
    place_type = Column(String(50), nullable=False, comment="장소 유형")
    place_address = Column(String(500), comment="장소 주소")
    
    latitude = Column(Float, nullable=False, comment="위도")
    longitude = Column(Float, nullable=False, comment="경도")
    
    distance_km = Column(Float, nullable=False, comment="실종 위치로부터의 거리 (km)")
    hotzone_score = Column(Float, nullable=False, comment="핫존 점수")
    
    # 장소별 가중치 정보 (JSON 형태로 저장)
    usage_weight = Column(Float, comment="이용도 가중치")
    danger_weight = Column(Float, comment="위험도 가중치")
    
    # MissingChild와의 관계
    missing_child = relationship("MissingChild", back_populates="hotzones")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Notice(Base):
    """공지사항 테이블"""
    __tablename__ = "notices"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="공지사항 제목")
    content = Column(Text, nullable=False, comment="공지사항 내용")
    
    # 공지사항 유형
    notice_type = Column(String(50), default="general", comment="공지사항 유형")
    
    # 중요도
    priority = Column(Integer, default=1, comment="중요도 (1-5)")
    
    # 활성화 상태
    is_active = Column(Boolean, default=True, comment="활성화 상태")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EmergencyContact(Base):
    """긴급 연락처 테이블"""
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="연락처명")
    phone_number = Column(String(20), nullable=False, comment="전화번호")
    description = Column(String(200), comment="설명")
    
    # 연락처 유형
    contact_type = Column(String(50), nullable=False, comment="연락처 유형 (emergency/center)")
    
    # 활성화 상태
    is_active = Column(Boolean, default=True, comment="활성화 상태")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
