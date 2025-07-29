# 실종아동 찾기 백엔드 - 팀 프레젠테이션

## 🎯 프로젝트 개요

### 목표
- 실종아동 찾기를 위한 핫존 생성 시스템
- 나이대별 맞춤 핫존 알고리즘
- 사용자 정보 관리 및 공지사항 시스템

### 핵심 기능
1. **사용자 정보 관리** (보호자 + 아이 정보)
2. **핫존 생성** (나이대별 맞춤 알고리즘)
3. **공지사항 관리**
4. **긴급 연락처** (112, 182)

## 🗂️ 프로젝트 구조

```
missing_children_backend/
├── app/
│   ├── database/          # 데이터베이스 연결
│   │   └── database.py
│   ├── models/           # SQLAlchemy 모델
│   │   └── models.py
│   ├── schemas/          # Pydantic 스키마
│   │   └── schemas.py
│   └── services/         # 핫존 생성 로직
│       └── hotzone_service.py
├── main.py               # FastAPI 애플리케이션
├── init_db.py            # 데이터베이스 초기화
└── README.md             # 프로젝트 문서
```

## 🗄️ 데이터베이스 설계

### 테이블 구조

#### 1. User 테이블 (사용자 정보)
```sql
- guardian_name: 보호자 성명
- guardian_phone: 보호자 연락처
- child_name: 아이 이름
- child_gender: 아이 성별
- child_birth_date: 아이 생년월일
- child_characteristics: 아이 특징
- child_height: 아이 키
- child_weight: 아이 몸무게
- child_clothing: 아이 옷차림
```

#### 2. FrequentPlace 테이블 (자주 가는 곳)
```sql
- place1_name ~ place4_name: 자주 가는 곳 4곳
- 각 장소별 주소, 위도, 경도 정보
```

#### 3. MissingChild 테이블 (실종아동 정보)
```sql
- missing_date: 실종 날짜
- missing_location: 실종 위치
- missing_latitude/longitude: 실종 위치 좌표
- child_age: 실종 당시 나이
- status: 실종 상태 (missing/found)
```

#### 4. Hotzone 테이블 (핫존 정보)
```sql
- place_name: 장소명
- place_type: 장소 유형
- latitude/longitude: 좌표
- distance_km: 실종 위치로부터 거리
- hotzone_score: 핫존 점수
- usage_weight: 이용도 가중치
- danger_weight: 위험도 가중치
```

#### 5. Notice 테이블 (공지사항)
#### 6. EmergencyContact 테이블 (긴급 연락처)

## 🧠 핵심 알고리즘: 나이대별 핫존 생성

### 나이대별 설정

| 나이대 | 반경 | 주요 장소 유형 |
|--------|------|----------------|
| 1-4세 | 1km | 놀이터, 공원, 유치원, 학교, 키즈카페 |
| 5-8세 | 1.3km | 놀이터, 공원, 유치원, 학교, 주거지역 |
| 9-11세 | 3.2km | 놀이터, 공원, 학교, 주거지역 |
| 12-14세 | 8km | 공원, 학교, 대학, 상업시설 |
| 15-16세 | 23km | 학교, 대학, 대중교통, 상업시설 |

### 핫존 점수 계산 공식
```
이용도 점수 = 장소별 가중치 / (거리 + 0.1)
위험도 점수 = 장소별 위험도 가중치 × (거리 + 1)
최종 핫존 점수 = 이용도 점수 - 위험도 점수
```

## 🔌 API 엔드포인트

### 사용자 관리
- `POST /users/` - 사용자 정보 생성
- `GET /users/{user_id}` - 사용자 정보 조회
- `PUT /users/{user_id}` - 사용자 정보 수정

### 핫존 관리
- `POST /hotzones/create/` - 핫존 생성
- `GET /hotzones/{missing_child_id}` - 핫존 목록 조회

### 공지사항
- `GET /notices/` - 공지사항 목록
- `GET /notices/{notice_id}` - 공지사항 상세

### 긴급 연락처
- `GET /emergency-contacts/` - 긴급 연락처 목록

## 🚀 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화
```bash
python init_db.py
```

### 3. 서버 실행
```bash
python main.py
```

## 📊 데이터베이스 확인

### 생성된 테이블
```bash
sqlite3 missing_children.db ".tables"
```

### 샘플 데이터 확인
```bash
sqlite3 missing_children.db "SELECT * FROM emergency_contacts;"
sqlite3 missing_children.db "SELECT * FROM notices;"
```

## 🎯 다음 단계

1. **프론트엔드 연동**: React Native 앱과 API 연동
2. **핫존 시각화**: 지도 위 핫존 표시 기능
3. **실시간 업데이트**: 실종아동 정보 실시간 동기화
4. **알림 시스템**: 핫존 발견 시 알림 기능

## 💡 기술 스택

- **Backend**: FastAPI, SQLAlchemy
- **Database**: SQLite (개발) / PostgreSQL (운영)
- **Geocoding**: Geopy, Nominatim
- **Map Data**: OSMnx, OpenStreetMap
- **Validation**: Pydantic
