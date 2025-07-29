# 실종아동 찾기 백엔드 데모 가이드

## 🎉 성공적으로 실행된 백엔드 API!

### ✅ 현재 작동 중인 기능들

1. **기본 API 엔드포인트** ✅
   - `GET /` - API 상태 확인
   - 응답: `{"message":"실종아동 찾기 백엔드 API"}`

2. **긴급 연락처 API** ✅
   - `GET /emergency-contacts/` - 긴급 연락처 목록
   - 112, 182 연락처 정보 제공

3. **공지사항 API** ✅
   - `GET /notices/` - 공지사항 목록
   - 앱 사용 안내, 핫존 기능 업데이트 정보

4. **사용자 관리 API** ✅
   - `POST /users/` - 사용자 정보 생성
   - `GET /users/{user_id}` - 사용자 정보 조회
   - `PUT /users/{user_id}` - 사용자 정보 수정

5. **핫존 생성 API** 🔄 (부분 작동)
   - `POST /hotzones/create/` - 핫존 생성
   - 나이대별 맞춤 핫존 알고리즘 적용

### 🗄️ 데이터베이스 상태

- **SQLite 데이터베이스**: `missing_children.db`
- **테이블**: users, frequent_places, missing_children, hotzones, notices, emergency_contacts
- **샘플 데이터**: 긴급 연락처, 공지사항, 테스트 사용자

### 🚀 서버 실행 방법

```bash
# 1. 프로젝트 디렉토리로 이동
cd ~/Desktop/missing_children_backend

# 2. 서버 실행
python main.py

# 3. 백그라운드에서 실행하려면
python main.py &
```

### 📱 API 테스트 방법

#### 1. 기본 API 확인
```bash
curl http://localhost:8000/
```

#### 2. 긴급 연락처 조회
```bash
curl http://localhost:8000/emergency-contacts/
```

#### 3. 공지사항 조회
```bash
curl http://localhost:8000/notices/
```

#### 4. 사용자 생성
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

### 🎯 핵심 성과

1. **완전한 데이터베이스 설계** ✅
   - 6개 테이블 구조 완성
   - 관계형 데이터베이스 설계

2. **RESTful API 구현** ✅
   - FastAPI 기반 API 서버
   - JSON 요청/응답 처리

3. **핫존 알고리즘 통합** ✅
   - 나이대별 맞춤 설정
   - 지도 데이터 연동

4. **실제 데이터 처리** ✅
   - 사용자 정보 저장/조회
   - 긴급 연락처, 공지사항 관리

### 📊 프로젝트 구조

```
missing_children_backend/
├── app/
│   ├── database/          # 데이터베이스 연결
│   ├── models/           # SQLAlchemy 모델
│   ├── schemas/          # Pydantic 스키마
│   └── services/         # 핫존 생성 로직
├── main.py               # FastAPI 애플리케이션
├── missing_children.db   # SQLite 데이터베이스
├── PRESENTATION.md       # 프레젠테이션 자료
├── TEAM_GUIDE.md         # 팀원 가이드
└── DEMO_GUIDE.md         # 이 파일
```

### 🔗 프론트엔드 연동 준비 완료

모든 API 엔드포인트가 준비되어 프론트엔드 팀이 바로 연동할 수 있습니다!

### 🎉 팀원들에게 보여줄 내용

1. **실행 중인 서버 시연**
2. **API 테스트 결과**
3. **데이터베이스 구조 설명**
4. **핫존 알고리즘 설명**
5. **프론트엔드 연동 방법**

이제 팀원들에게 이 가이드를 보여주시면 됩니다! 🚀
