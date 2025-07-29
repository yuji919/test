# 사용자 정보 입력 API 문서

## 개요
실종아동 찾기 시스템에서 사용자(보호자) 정보를 단계별로 입력할 수 있는 API입니다.

## API 엔드포인트

### 1. 단계별 사용자 정보 입력

#### 1단계: 보호자 기본 정보 입력
```http
POST /user-info/step1/
```

**요청 본문:**
```json
{
  "guardian_name": "김철수",
  "guardian_phone": "010-1234-5678"
}
```

**응답:**
```json
{
  "user_id": 1,
  "step": "step1_complete",
  "is_complete": false,
  "message": "보호자 정보가 성공적으로 입력되었습니다. 다음 단계로 진행해주세요."
}
```

#### 2단계: 아이 기본 정보 입력
```http
PUT /user-info/{user_id}/step2/
```

**요청 본문:**
```json
{
  "child_name": "김민수",
  "child_gender": "남",
  "child_birth_date": "2015-03-15"
}
```

#### 3단계: 아이 상세 정보 입력
```http
PUT /user-info/{user_id}/step3/
```

**요청 본문:**
```json
{
  "child_characteristics": "검은 머리, 큰 눈, 키 120cm",
  "child_height": 120.0,
  "child_weight": 25.5,
  "child_clothing": "파란색 상의, 검은색 바지, 흰색 운동화"
}
```

#### 4단계: 자주 가는 곳 정보 입력
```http
PUT /user-info/{user_id}/step4/
```

**요청 본문:**
```json
{
  "places": [
    {
      "name": "집",
      "address": "서울시 강남구 테헤란로 123",
      "latitude": 37.5665,
      "longitude": 126.9780
    },
    {
      "name": "학교",
      "address": "서울시 강남구 역삼동 456",
      "latitude": 37.5666,
      "longitude": 126.9781
    }
  ]
}
```

#### 5단계: 실종 정보 입력 (선택사항)
```http
PUT /user-info/{user_id}/step5/
```

**요청 본문:**
```json
{
  "missing_date": "2024-01-15T14:30:00",
  "missing_location": "서울시 강남구 테헤란로 123",
  "missing_latitude": 37.5665,
  "missing_longitude": 126.9780,
  "child_age": 8,
  "child_description": "오후 3시경 집에서 실종"
}
```

### 2. 한 번에 모든 정보 입력

```http
POST /user-info/complete/
```

**요청 본문:**
```json
{
  "guardian_info": {
    "guardian_name": "이영희",
    "guardian_phone": "010-9876-5432"
  },
  "child_basic_info": {
    "child_name": "이지은",
    "child_gender": "여",
    "child_birth_date": "2016-07-20"
  },
  "child_detail_info": {
    "child_characteristics": "갈색 머리, 작은 키, 활발함",
    "child_height": 115.0,
    "child_weight": 22.0,
    "child_clothing": "분홍색 원피스, 흰색 양말"
  },
  "frequent_places_info": {
    "places": [
      {
        "name": "집",
        "address": "서울시 서초구 서초대로 456",
        "latitude": 37.5668,
        "longitude": 126.9783
      }
    ]
  },
  "missing_info": {
    "missing_date": "2024-01-15T09:00:00",
    "missing_location": "서울시 서초구 서초대로 456",
    "missing_latitude": 37.5668,
    "missing_longitude": 126.9783,
    "child_age": 7,
    "child_description": "오전 9시경 유치원 등원 중 실종"
  }
}
```

### 3. 진행 상황 조회

```http
GET /user-info/{user_id}/progress/
```

**응답:**
```json
{
  "user_id": 1,
  "current_step": "step3",
  "progress": {
    "step1": true,
    "step2": true,
    "step3": true,
    "step4": false,
    "step5": false
  },
  "is_complete": false
}
```

## 입력 단계별 설명

### 1단계: 보호자 기본 정보
- **guardian_name**: 보호자 성명 (필수)
- **guardian_phone**: 보호자 연락처 (필수)

### 2단계: 아이 기본 정보
- **child_name**: 아이 이름 (필수)
- **child_gender**: 아이 성별 - "남" 또는 "여" (필수)
- **child_birth_date**: 아이 생년월일 (필수)

### 3단계: 아이 상세 정보 (선택사항)
- **child_characteristics**: 아이 특징 (선택)
- **child_height**: 아이 키 (cm) (선택)
- **child_weight**: 아이 몸무게 (kg) (선택)
- **child_clothing**: 아이 옷차림 (선택)

### 4단계: 자주 가는 곳 정보 (선택사항)
- **places**: 자주 가는 곳 목록 (최대 4개)
  - **name**: 장소명 (필수)
  - **address**: 주소 (선택)
  - **latitude**: 위도 (선택)
  - **longitude**: 경도 (선택)

### 5단계: 실종 정보 (선택사항)
- **missing_date**: 실종 날짜 (선택)
- **missing_location**: 실종 위치 (선택)
- **missing_latitude**: 실종 위치 위도 (선택)
- **missing_longitude**: 실종 위치 경도 (선택)
- **child_age**: 실종 당시 나이 (선택)
- **child_description**: 추가 설명 (선택)

## 사용 예시

### Python requests를 사용한 예시

```python
import requests

# 1단계: 보호자 정보 입력
guardian_info = {
    "guardian_name": "김철수",
    "guardian_phone": "010-1234-5678"
}

response = requests.post("http://localhost:8000/user-info/step1/", json=guardian_info)
result = response.json()
user_id = result["user_id"]

# 2단계: 아이 기본 정보 입력
child_basic_info = {
    "child_name": "김민수",
    "child_gender": "남",
    "child_birth_date": "2015-03-15"
}

response = requests.put(f"http://localhost:8000/user-info/{user_id}/step2/", json=child_basic_info)

# 진행 상황 조회
response = requests.get(f"http://localhost:8000/user-info/{user_id}/progress/")
progress = response.json()
print(f"현재 단계: {progress['current_step']}")
```

## 오류 응답

모든 API는 오류 발생 시 다음과 같은 형식으로 응답합니다:

```json
{
  "detail": "오류 메시지"
}
```

## 테스트

테스트 파일 `test_user_info.py`를 실행하여 모든 API를 테스트할 수 있습니다:

```bash
python test_user_info.py
``` 