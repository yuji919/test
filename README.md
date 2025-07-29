# 실종아동 찾기 백엔드 API

실종아동 찾기를 위한 핫존 생성 및 사용자 정보 관리 백엔드 API입니다.

## 🚀 주요 기능

- **사용자 정보 관리**: 보호자 및 아이 정보 단계별 입력
- **사진 업로드**: 프로필, 실종 증거, 기타 증거 사진 관리
- **핫존 생성**: 나이대별 맞춤 핫존 알고리즘
- **공지사항 관리**: 앱 사용 안내 및 업데이트 정보
- **긴급 연락처**: 112, 182 등 긴급 연락처 정보

## 📋 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Image Processing**: Pillow
- **File Upload**: python-multipart

## 🛠️ 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/missing-children-backend.git
cd missing-children-backend
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 초기화
```bash
python init_db.py
```

### 5. 서버 실행
```bash
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

## 📚 API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 API 엔드포인트

### 사용자 정보 입력
- `POST /user-info/step1/` - 보호자 기본 정보
- `PUT /user-info/{user_id}/step2/` - 아이 기본 정보
- `PUT /user-info/{user_id}/step3/` - 아이 상세 정보
- `PUT /user-info/{user_id}/step4/` - 자주 가는 곳
- `PUT /user-info/{user_id}/step5/` - 실종 정보
- `GET /user-info/{user_id}/progress/` - 진행 상황 조회

### 사진 업로드
- `POST /photos/upload/{user_id}` - 사진 업로드
- `GET /photos/user/{user_id}` - 사용자 사진 목록
- `PUT /photos/{photo_id}` - 사진 정보 수정
- `DELETE /photos/{photo_id}` - 사진 삭제

### 기타 API
- `GET /emergency-contacts/` - 긴급 연락처
- `GET /notices/` - 공지사항
- `POST /hotzones/create/` - 핫존 생성

## 📁 프로젝트 구조

```
missing_children_backend/
├── app/
│   ├── database/          # 데이터베이스 연결
│   ├── models/           # SQLAlchemy 모델
│   ├── schemas/          # Pydantic 스키마
│   └── services/         # 비즈니스 로직
├── main.py               # FastAPI 애플리케이션
├── init_db.py            # 데이터베이스 초기화
├── requirements.txt      # Python 의존성
└── README.md            # 프로젝트 문서
```

## 🔗 프론트엔드 연동

프론트엔드 연동을 위한 상세 가이드는 다음 문서를 참고하세요:
- [프론트엔드 연동 가이드](FRONTEND_INTEGRATION_GUIDE.md)
- [API 엔드포인트 요약](API_ENDPOINTS_SUMMARY.md)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.
