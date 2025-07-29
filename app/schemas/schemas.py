from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# User 관련 스키마 (간단한 내정보 등록)
class UserBase(BaseModel):
    name: str = Field(..., description="성명")
    phone: str = Field(..., description="연락처")
    age: int = Field(..., description="나이")
    gender: str = Field(..., description="성별 (남/여)")
    missing_location: str = Field(..., description="실종 위치")

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# FrequentPlace 관련 스키마
class FrequentPlaceBase(BaseModel):
    place1_name: Optional[str] = Field(None, description="자주 가는 곳 1")
    place1_address: Optional[str] = Field(None, description="자주 가는 곳 1 주소")
    place1_latitude: Optional[float] = Field(None, description="자주 가는 곳 1 위도")
    place1_longitude: Optional[float] = Field(None, description="자주 가는 곳 1 경도")
    
    place2_name: Optional[str] = Field(None, description="자주 가는 곳 2")
    place2_address: Optional[str] = Field(None, description="자주 가는 곳 2 주소")
    place2_latitude: Optional[float] = Field(None, description="자주 가는 곳 2 위도")
    place2_longitude: Optional[float] = Field(None, description="자주 가는 곳 2 경도")
    
    place3_name: Optional[str] = Field(None, description="자주 가는 곳 3")
    place3_address: Optional[str] = Field(None, description="자주 가는 곳 3 주소")
    place3_latitude: Optional[float] = Field(None, description="자주 가는 곳 3 위도")
    place3_longitude: Optional[float] = Field(None, description="자주 가는 곳 3 경도")
    
    place4_name: Optional[str] = Field(None, description="자주 가는 곳 4")
    place4_address: Optional[str] = Field(None, description="자주 가는 곳 4 주소")
    place4_latitude: Optional[float] = Field(None, description="자주 가는 곳 4 위도")
    place4_longitude: Optional[float] = Field(None, description="자주 가는 곳 4 경도")

class FrequentPlaceCreate(FrequentPlaceBase):
    user_id: int

class FrequentPlaceUpdate(FrequentPlaceBase):
    pass

class FrequentPlace(FrequentPlaceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# MissingChild 관련 스키마
class MissingChildBase(BaseModel):
    missing_date: datetime = Field(..., description="실종 날짜")
    missing_location: str = Field(..., description="실종 위치")
    missing_latitude: Optional[float] = Field(None, description="실종 위치 위도")
    missing_longitude: Optional[float] = Field(None, description="실종 위치 경도")
    child_age: int = Field(..., description="실종 당시 나이")
    child_description: Optional[str] = Field(None, description="추가 설명")

class MissingChildCreate(MissingChildBase):
    user_id: int

class MissingChildUpdate(MissingChildBase):
    status: Optional[str] = Field("missing", description="상태 (missing/found)")

class MissingChild(MissingChildBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Hotzone 관련 스키마
class HotzoneBase(BaseModel):
    place_name: str = Field(..., description="장소명")
    place_type: str = Field(..., description="장소 유형")
    place_address: Optional[str] = Field(None, description="장소 주소")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    distance_km: float = Field(..., description="실종 위치로부터의 거리 (km)")
    hotzone_score: float = Field(..., description="핫존 점수")
    usage_weight: Optional[float] = Field(None, description="이용도 가중치")
    danger_weight: Optional[float] = Field(None, description="위험도 가중치")

class HotzoneCreate(HotzoneBase):
    missing_child_id: int

class HotzoneUpdate(HotzoneBase):
    pass

class Hotzone(HotzoneBase):
    id: int
    missing_child_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Notice 관련 스키마
class NoticeBase(BaseModel):
    title: str = Field(..., description="공지사항 제목")
    content: str = Field(..., description="공지사항 내용")
    notice_type: str = Field("general", description="공지사항 유형")
    priority: int = Field(1, description="중요도 (1-5)")
    is_active: bool = Field(True, description="활성화 상태")

class NoticeCreate(NoticeBase):
    pass

class NoticeUpdate(NoticeBase):
    pass

class Notice(NoticeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# EmergencyContact 관련 스키마
class EmergencyContactBase(BaseModel):
    name: str = Field(..., description="연락처명")
    phone_number: str = Field(..., description="전화번호")
    description: Optional[str] = Field(None, description="설명")
    contact_type: str = Field(..., description="연락처 유형 (emergency/center)")
    is_active: bool = Field(True, description="활성화 상태")

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactUpdate(EmergencyContactBase):
    pass

class EmergencyContact(EmergencyContactBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 핫존 생성 요청 스키마
class HotzoneRequest(BaseModel):
    user_id: int = Field(..., description="사용자 ID")
    missing_location: str = Field(..., description="실종 위치")
    child_age: int = Field(..., description="아이 나이")
    radius_km: Optional[float] = Field(None, description="검색 반경 (km)")

# 핫존 생성 응답 스키마
class HotzoneResponse(BaseModel):
    missing_child_id: int
    hotzones: List[Hotzone]
    total_count: int
    search_radius: float
    
    class Config:
        from_attributes = True

# 사용자 정보 입력을 위한 단계별 스키마
class GuardianInfo(BaseModel):
    """1단계: 보호자 기본 정보"""
    guardian_name: str = Field(..., description="보호자 성명")
    guardian_phone: str = Field(..., description="보호자 연락처")

class ChildBasicInfo(BaseModel):
    """2단계: 아이 기본 정보"""
    child_name: str = Field(..., description="아이 이름")
    child_gender: str = Field(..., description="아이 성별 (남/여)")
    child_birth_date: str = Field(..., description="아이 생년월일")

class ChildDetailInfo(BaseModel):
    """3단계: 아이 상세 정보"""
    child_characteristics: Optional[str] = Field(None, description="아이 특징")
    child_height: Optional[float] = Field(None, description="아이 키 (cm)")
    child_weight: Optional[float] = Field(None, description="아이 몸무게 (kg)")
    child_clothing: Optional[str] = Field(None, description="아이 옷차림")

class PlaceInfo(BaseModel):
    """장소 정보"""
    name: str = Field(..., description="장소명")
    address: Optional[str] = Field(None, description="주소")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")

class FrequentPlacesInfo(BaseModel):
    """4단계: 자주 가는 곳 정보"""
    places: List[PlaceInfo] = Field(..., description="자주 가는 곳 목록 (최대 4개)")

class MissingInfo(BaseModel):
    """5단계: 실종 정보 (선택사항)"""
    missing_date: Optional[datetime] = Field(None, description="실종 날짜")
    missing_location: Optional[str] = Field(None, description="실종 위치")
    missing_latitude: Optional[float] = Field(None, description="실종 위치 위도")
    missing_longitude: Optional[float] = Field(None, description="실종 위치 경도")
    child_age: Optional[int] = Field(None, description="실종 당시 나이")
    child_description: Optional[str] = Field(None, description="추가 설명")

# 통합 사용자 정보 입력 스키마
class CompleteUserInfo(BaseModel):
    """전체 사용자 정보 입력"""
    guardian_info: GuardianInfo
    child_basic_info: ChildBasicInfo
    child_detail_info: Optional[ChildDetailInfo] = None
    frequent_places_info: Optional[FrequentPlacesInfo] = None
    missing_info: Optional[MissingInfo] = None

# 사용자 정보 입력 응답 스키마
class UserInfoResponse(BaseModel):
    """사용자 정보 입력 응답"""
    user_id: int
    step: str = Field(..., description="현재 단계")
    is_complete: bool = Field(..., description="입력 완료 여부")
    message: str = Field(..., description="응답 메시지")

# Photo 관련 스키마
class PhotoBase(BaseModel):
    """사진 기본 정보"""
    image_type: str = Field(..., description="이미지 타입 (profile/missing/evidence)")
    description: Optional[str] = Field(None, description="사진 설명")
    is_primary: bool = Field(False, description="대표 사진 여부")

class PhotoCreate(PhotoBase):
    """사진 생성 스키마"""
    pass

class PhotoUpdate(BaseModel):
    """사진 수정 스키마"""
    image_type: Optional[str] = Field(None, description="이미지 타입 (profile/missing/evidence)")
    description: Optional[str] = Field(None, description="사진 설명")
    is_primary: Optional[bool] = Field(None, description="대표 사진 여부")
    is_active: Optional[bool] = Field(None, description="활성화 상태")

class Photo(PhotoBase):
    """사진 응답 스키마"""
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 사진 업로드 응답 스키마
class PhotoUploadResponse(BaseModel):
    """사진 업로드 응답"""
    photo_id: int
    filename: str
    file_path: str
    file_size: int
    message: str

# 사용자 정보에 사진 포함
class UserWithPhotos(User):
    """사진이 포함된 사용자 정보"""
    photos: List[Photo] = []

# 사진 업로드 요청 스키마
class PhotoUploadRequest(BaseModel):
    """사진 업로드 요청"""
    image_type: str = Field(..., description="이미지 타입")
    description: Optional[str] = Field(None, description="사진 설명")
    is_primary: bool = Field(False, description="대표 사진 여부")
