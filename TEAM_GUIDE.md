# 팀원을 위한 빠른 시작 가이드

## 🚀 5분 만에 백엔드 실행하기

### 1. 프로젝트 클론/다운로드
```bash
# 프로젝트 폴더로 이동
cd missing_children_backend
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 초기화
```bash
python init_db.py
```

### 4. 서버 실행
```bash
python main.py
```

### 5. API 테스트
```bash
python test_api.py
```

## 📊 데이터베이스 확인

### 테이블 목록 확인
```bash
sqlite3 missing_children.db ".tables"
```

### 샘플 데이터 확인
```bash
# 긴급 연락처 확인
sqlite3 missing_children.db "SELECT * FROM emergency_contacts;"

# 공지사항 확인
sqlite3 missing_children.db "SELECT * FROM notices;"
```

## 🔍 주요 파일 설명

### 핵심 파일들
- `main.py` - FastAPI 메인 애플리케이션
- `app/models/models.py` - 데이터베이스 테이블 구조
- `app/services/hotzone_service.py` - 핫존 생성 알고리즘
- `app/schemas/schemas.py` - API 요청/응답 형식

### 설정 파일들
- `requirements.txt` - Python 패키지 목록
- `init_db.py` - 데이터베이스 초기화 스크립트
- `test_api.py` - API 테스트 스크립트

## 🎯 핵심 기능 테스트

### 1. 긴급 연락처 조회
```bash
curl http://localhost:8000/emergency-contacts/
```

### 2. 공지사항 조회
```bash
curl http://localhost:8000/notices/
```

### 3. 사용자 생성
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "guardian_name": "김보호",
    "guardian_phone": "010-1234-5678",
    "child_name": "김아이",
    "child_gender": "남",
    "child_birth_date": "2018-05-15"
  }'
```

### 4. 핫존 생성
```bash
curl -X POST http://localhost:8000/hotzones/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "missing_location": "서울특별시 강남구 역삼동",
    "child_age": 7
  }'
```

## 📱 프론트엔드 연동 예시

### React Native에서 API 호출
```javascript
// 긴급 연락처 조회
const getEmergencyContacts = async () => {
  const response = await fetch('http://localhost:8000/emergency-contacts/');
  const contacts = await response.json();
  return contacts;
};

// 핫존 생성
const createHotzones = async (userData) => {
  const response = await fetch('http://localhost:8000/hotzones/create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData)
  });
  const result = await response.json();
  return result;
};
```

## 🐛 문제 해결

### 서버가 실행되지 않을 때
1. 포트 8000이 사용 중인지 확인
2. `python main.py` 명령어 재실행

### 데이터베이스 오류가 발생할 때
1. `python init_db.py` 재실행
2. `missing_children.db` 파일 삭제 후 재생성

### 패키지 설치 오류가 발생할 때
1. `pip install --upgrade pip`
2. `pip install -r requirements.txt` 재실행

## 📞 문의사항

백엔드 관련 문의사항이 있으면 팀원에게 연락하세요!
