# 실종아동 찾기 백엔드 API

실종아동 찾기를 위한 핫존 생성 및 관리 백엔드 API입니다.

## 프로젝트 구조

```
missing_children_backend/
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py          # 데이터베이스 연결 설정
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # SQLAlchemy 모델 정의
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic 스키마 정의
│   └── services/
│       ├── __init__.py
│       └── hotzone_service.py   # 핫존 생성 로직
├── main.py                      # FastAPI 메인 애플리케이션
├── init_db.py                   # 데이터베이스 초기화 스크립트
├── requirements.txt              # Python 패키지 의존성
└── README.md                    # 프로젝트 설명서
```

## 데이터베이스 설계

### 1. User 테이블 (사용자 정보)
- 보호자 정보 (이름, 연락처)
- 아이 정보 (이름, 성별, 생년월일, 특징, 키, 몸무게, 옷차림)

### 2. FrequentPlace 테이블 (자주 가는 곳)
- 사용자별 자주 가는 곳 4곳 저장
- 각 장소의 이름, 주소, 좌표 정보

### 3. MissingChild 테이블 (실종아동 정보)
- 실종 날짜, 위치, 좌표
- 아이 나이, 추가 설명
- 실종 상태 (missing/found)

### 4. Hotzone 테이블 (핫존 정보)
- 실종아동별 핫존 장소 정보
- 장소명, 유형, 주소, 좌표
- 거리, 핫존 점수, 가중치 정보

### 5. Notice 테이블 (공지사항)
- 공지사항 제목, 내용
- 유형, 중요도, 활성화 상태

### 6. EmergencyContact 테이블 (긴급 연락처)
- 112, 182 등 긴급 연락처 정보
- 연락처명, 전화번호, 설명

## 핫존 생성 로직

### 나이대별 설정
1. **1-4세**: 반경 1km, 놀이터, 공원, 유치원, 학교, 키즈카페
2. **5-8세**: 반경 1.3km, 놀이터, 공원, 유치원, 학교, 주거지역
3. **9-11세**: 반경 3.2km, 놀이터, 공원, 학교, 주거지역
4. **12-14세**: 반경 8km, 공원, 학교, 대학, 상업시설
5. **15-16세**: 반경 23km, 학교, 대학, 대중교통, 상업시설

### 핫존 점수 계산
- **이용도 점수**: 장소별 가중치 / (거리 + 0.1)
- **위험도 점수**: 장소별 위험도 가중치 × (거리 + 1)
- **최종 점수**: 이용도 점수 - 위험도 점수

## 설치 및 실행

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

## API 엔드포인트

### 사용자 관리
- `POST /users/` - 사용자 정보 생성
- `GET /users/{user_id}` - 사용자 정보 조회
- `PUT /users/{user_id}` - 사용자 정보 수정

### 자주 가는 곳
- `POST /frequent-places/` - 자주 가는 곳 정보 생성
- `GET /frequent-places/{user_id}` - 자주 가는 곳 정보 조회

### 핫존 관리
- `POST /hotzones/create/` - 핫존 생성
- `GET /hotzones/{missing_child_id}` - 핫존 목록 조회

### 공지사항
- `GET /notices/` - 공지사항 목록 조회
- `GET /notices/{notice_id}` - 공지사항 상세 조회

### 긴급 연락처
- `GET /emergency-contacts/` - 긴급 연락처 목록 조회

## 핵심 기능

1. **사용자 정보 관리**: 보호자와 아이 정보 저장
2. **핫존 생성**: 나이대별 맞춤 핫존 생성
3. **공지사항 관리**: 실종아동 관련 공지사항 제공
4. **긴급 연락처**: 112, 182 등 긴급 연락처 정보 제공

## 기술 스택

- **Framework**: FastAPI
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Geocoding**: Geopy, Nominatim
- **Map Data**: OSMnx, OpenStreetMap
- **Validation**: Pydantic
