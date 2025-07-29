# GitHub 배포 가이드

## 🚀 GitHub에 코드 업로드하기

### 1. Git 저장소 초기화
```bash
# Git 저장소 초기화
git init

# 원격 저장소 추가 (GitHub 저장소 URL로 변경)
git remote add origin https://github.com/your-username/missing-children-backend.git
```

### 2. 파일 추가 및 커밋
```bash
# 모든 파일 추가
git add .

# 첫 번째 커밋
git commit -m "Initial commit: Missing Children Backend API"

# 메인 브랜치로 푸시
git push -u origin main
```

### 3. GitHub에서 확인할 파일들

#### ✅ 포함되는 파일들
```
missing_children_backend/
├── app/                          # 핵심 애플리케이션 코드
│   ├── __init__.py
│   ├── database/
│   ├── models/
│   ├── schemas/
│   └── services/
├── main.py                       # FastAPI 메인 애플리케이션
├── init_db.py                    # 데이터베이스 초기화
├── requirements.txt              # Python 의존성
├── README.md                     # 프로젝트 설명서
├── LICENSE                       # MIT 라이선스
├── .gitignore                    # Git 제외 파일 설정
├── FRONTEND_INTEGRATION_GUIDE.md # 프론트엔드 연동 가이드
├── API_ENDPOINTS_SUMMARY.md      # API 엔드포인트 요약
├── USER_INFO_API.md              # 사용자 정보 API 문서
├── PHOTO_UPLOAD_API.md           # 사진 업로드 API 문서
├── DEMO_GUIDE.md                 # 데모 가이드
├── TEAM_GUIDE.md                 # 팀 가이드
└── PRESENTATION.md               # 프레젠테이션
```

#### ❌ 제외되는 파일들 (.gitignore에 의해)
```
missing_children_backend/
├── missing_children.db           # 로컬 데이터베이스 (제외)
├── uploads/                      # 업로드된 파일들 (제외)
├── cache/                        # 캐시 파일들 (제외)
├── __pycache__/                  # Python 캐시 (제외)
└── .DS_Store                     # 시스템 파일 (제외)
```

### 4. GitHub 저장소 설정

#### Repository 이름
```
missing-children-backend
```

#### Description
```
실종아동 찾기를 위한 핫존 생성 및 사용자 정보 관리 백엔드 API
```

#### Topics (태그)
```
fastapi, python, sqlalchemy, missing-children, hotzone, api, backend
```

#### README 설정
- GitHub에서 자동으로 `README.md` 파일을 메인 페이지로 표시
- 설치 및 실행 방법이 명확히 작성됨

### 5. 추가 설정 (선택사항)

#### GitHub Actions (CI/CD)
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest
```

#### GitHub Pages (API 문서)
- `docs/` 폴더에 API 문서 추가
- GitHub Pages로 자동 문서화

### 6. 배포 후 확인사항

#### ✅ 확인할 점들
1. **README.md**가 GitHub에서 잘 보이는지
2. **requirements.txt**가 올바른지
3. **.gitignore**가 제대로 작동하는지
4. **LICENSE** 파일이 있는지
5. **프론트엔드 연동 문서**들이 포함되었는지

#### 🔧 추가 권장사항
1. **Issues 템플릿** 생성
2. **Pull Request 템플릿** 생성
3. **Contributing 가이드** 작성
4. **Code of Conduct** 추가

### 7. 배포 완료 후

#### 다른 개발자들이 사용할 수 있도록:
1. **README.md**에 명확한 설치 방법 제공
2. **API 문서** 링크 제공
3. **예제 코드** 포함
4. **라이선스** 명시

#### 프론트엔드 개발자를 위해:
1. **FRONTEND_INTEGRATION_GUIDE.md** 참조
2. **API_ENDPOINTS_SUMMARY.md** 참조
3. **실제 API 테스트** 가능하도록 샘플 데이터 포함

이제 GitHub에 깔끔하게 정리된 코드가 업로드됩니다! 🎉 