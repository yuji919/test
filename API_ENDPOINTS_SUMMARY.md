# API 엔드포인트 요약

## 🚀 기본 정보
- **Base URL**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs`

## 📋 사용자 정보 입력 API

### 단계별 입력
| 단계 | 메서드 | 엔드포인트 | 설명 |
|------|--------|------------|------|
| 1단계 | POST | `/user-info/step1/` | 보호자 기본 정보 |
| 2단계 | PUT | `/user-info/{user_id}/step2/` | 아이 기본 정보 |
| 3단계 | PUT | `/user-info/{user_id}/step3/` | 아이 상세 정보 |
| 4단계 | PUT | `/user-info/{user_id}/step4/` | 자주 가는 곳 |
| 5단계 | PUT | `/user-info/{user_id}/step5/` | 실종 정보 |

### 통합 입력
| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/user-info/complete/` | 모든 정보 한 번에 입력 |

### 진행 상황
| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| GET | `/user-info/{user_id}/progress/` | 진행 상황 조회 |

## 📸 사진 업로드 API

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/photos/upload/{user_id}` | 사진 업로드 |
| GET | `/photos/user/{user_id}` | 사용자 사진 목록 |
| GET | `/photos/{photo_id}` | 사진 상세 조회 |
| PUT | `/photos/{photo_id}` | 사진 정보 수정 |
| DELETE | `/photos/{photo_id}` | 사진 삭제 |
| GET | `/photos/{user_id}/{filename}` | 사진 파일 접근 |

## 🔧 기존 API (참고용)

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| GET | `/users/{user_id}` | 사용자 정보 조회 |
| PUT | `/users/{user_id}` | 사용자 정보 수정 |
| GET | `/frequent-places/{user_id}` | 자주 가는 곳 조회 |
| POST | `/hotzones/create/` | 핫존 생성 |
| GET | `/hotzones/{missing_child_id}` | 핫존 목록 조회 |

## 📊 응답 형식

### 성공 응답
```json
{
  "user_id": 1,
  "step": "step1_complete",
  "is_complete": false,
  "message": "보호자 정보가 성공적으로 입력되었습니다."
}
```

### 사진 업로드 응답
```json
{
  "photo_id": 1,
  "filename": "uuid-filename.jpg",
  "file_path": "uploads/1/uuid-filename.jpg",
  "file_size": 123456,
  "message": "사진이 성공적으로 업로드되었습니다."
}
```

### 에러 응답
```json
{
  "detail": "에러 메시지"
}
```

## 🌐 프론트엔드 연동 예시

### JavaScript Fetch API
```javascript
// 사용자 정보 입력
const createUser = async (userData) => {
  const response = await fetch('http://localhost:8000/user-info/step1/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  return await response.json();
};

// 사진 업로드
const uploadPhoto = async (userId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('image_type', 'profile');
  formData.append('description', '프로필 사진');
  formData.append('is_primary', 'true');
  
  const response = await fetch(`http://localhost:8000/photos/upload/${userId}`, {
    method: 'POST',
    body: formData
  });
  return await response.json();
};
```

### React Hook 예시
```javascript
import { useState, useEffect } from 'react';

const useUserInfo = (userId) => {
  const [userProgress, setUserProgress] = useState(null);
  const [loading, setLoading] = useState(false);

  const getUserProgress = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/user-info/${userId}/progress/`);
      const data = await response.json();
      setUserProgress(data);
    } catch (error) {
      console.error('진행 상황 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      getUserProgress();
    }
  }, [userId]);

  return { userProgress, loading, refetch: getUserProgress };
};
```

## 📱 모바일 앱 연동

### React Native
```javascript
// 사진 업로드 (React Native)
const uploadPhotoFromMobile = async (userId, imageUri) => {
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'photo.jpg',
  });
  formData.append('image_type', 'profile');
  formData.append('description', '모바일에서 업로드');
  formData.append('is_primary', 'true');

  const response = await fetch(`http://localhost:8000/photos/upload/${userId}`, {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return await response.json();
};
```

## 🔒 CORS 설정 (백엔드)

프론트엔드에서 API 호출 시 CORS 오류가 발생하면 백엔드에 다음 설정 추가:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 배포 시 변경사항

1. **Base URL 변경**: `http://localhost:8000` → 프로덕션 서버 URL
2. **HTTPS 사용**: 보안을 위해 HTTPS 필수
3. **CORS 설정**: 특정 도메인만 허용
4. **에러 처리**: 사용자 친화적인 에러 메시지

이 요약을 참고하여 프론트엔드 개발을 시작하세요! 🎯 