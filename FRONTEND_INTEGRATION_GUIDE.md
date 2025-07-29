# 프론트엔드 연동 가이드

## 🚀 API 기본 정보

### 서버 정보
- **Base URL**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs`
- **Content-Type**: `application/json` (일반 API), `multipart/form-data` (파일 업로드)

## 📋 사용자 정보 입력 API

### 1. 단계별 사용자 정보 입력

#### 1단계: 보호자 기본 정보
```javascript
// JavaScript/React 예시
const createGuardianInfo = async (guardianData) => {
  const response = await fetch('http://localhost:8000/user-info/step1/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      guardian_name: guardianData.name,
      guardian_phone: guardianData.phone
    })
  });
  
  return await response.json();
};
```

#### 2단계: 아이 기본 정보
```javascript
const updateChildBasicInfo = async (userId, childData) => {
  const response = await fetch(`http://localhost:8000/user-info/${userId}/step2/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      child_name: childData.name,
      child_gender: childData.gender,
      child_birth_date: childData.birthDate
    })
  });
  
  return await response.json();
};
```

#### 3단계: 아이 상세 정보
```javascript
const updateChildDetailInfo = async (userId, detailData) => {
  const response = await fetch(`http://localhost:8000/user-info/${userId}/step3/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      child_characteristics: detailData.characteristics,
      child_height: detailData.height,
      child_weight: detailData.weight,
      child_clothing: detailData.clothing
    })
  });
  
  return await response.json();
};
```

#### 4단계: 자주 가는 곳 정보
```javascript
const updateFrequentPlaces = async (userId, placesData) => {
  const response = await fetch(`http://localhost:8000/user-info/${userId}/step4/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      places: placesData.map(place => ({
        name: place.name,
        address: place.address,
        latitude: place.latitude,
        longitude: place.longitude
      }))
    })
  });
  
  return await response.json();
};
```

#### 5단계: 실종 정보 (선택사항)
```javascript
const updateMissingInfo = async (userId, missingData) => {
  const response = await fetch(`http://localhost:8000/user-info/${userId}/step5/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      missing_date: missingData.date,
      missing_location: missingData.location,
      missing_latitude: missingData.latitude,
      missing_longitude: missingData.longitude,
      child_age: missingData.age,
      child_description: missingData.description
    })
  });
  
  return await response.json();
};
```

### 2. 진행 상황 조회
```javascript
const getUserProgress = async (userId) => {
  const response = await fetch(`http://localhost:8000/user-info/${userId}/progress/`);
  return await response.json();
};
```

### 3. 한 번에 모든 정보 입력
```javascript
const createCompleteUserInfo = async (completeData) => {
  const response = await fetch('http://localhost:8000/user-info/complete/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      guardian_info: completeData.guardian,
      child_basic_info: completeData.childBasic,
      child_detail_info: completeData.childDetail,
      frequent_places_info: completeData.places,
      missing_info: completeData.missing
    })
  });
  
  return await response.json();
};
```

## 📸 사진 업로드 API

### 1. 사진 업로드
```javascript
const uploadPhoto = async (userId, file, photoData) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('image_type', photoData.type);
  formData.append('description', photoData.description);
  formData.append('is_primary', photoData.isPrimary);
  
  const response = await fetch(`http://localhost:8000/photos/upload/${userId}`, {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};
```

### 2. 사진 목록 조회
```javascript
const getUserPhotos = async (userId) => {
  const response = await fetch(`http://localhost:8000/photos/user/${userId}`);
  return await response.json();
};
```

### 3. 사진 정보 수정
```javascript
const updatePhoto = async (photoId, photoData) => {
  const response = await fetch(`http://localhost:8000/photos/${photoId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_type: photoData.type,
      description: photoData.description,
      is_primary: photoData.isPrimary,
      is_active: photoData.isActive
    })
  });
  
  return await response.json();
};
```

### 4. 사진 삭제
```javascript
const deletePhoto = async (photoId) => {
  const response = await fetch(`http://localhost:8000/photos/${photoId}`, {
    method: 'DELETE'
  });
  
  return await response.json();
};
```

### 5. 사진 파일 접근
```javascript
const getPhotoUrl = (userId, filename) => {
  return `http://localhost:8000/photos/${userId}/${filename}`;
};
```

## 🔧 React 컴포넌트 예시

### 사용자 정보 입력 컴포넌트
```jsx
import React, { useState } from 'react';

const UserInfoForm = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [userId, setUserId] = useState(null);
  const [formData, setFormData] = useState({});

  const handleStep1 = async (guardianData) => {
    try {
      const result = await createGuardianInfo(guardianData);
      setUserId(result.user_id);
      setCurrentStep(2);
    } catch (error) {
      console.error('보호자 정보 입력 실패:', error);
    }
  };

  const handleStep2 = async (childData) => {
    try {
      await updateChildBasicInfo(userId, childData);
      setCurrentStep(3);
    } catch (error) {
      console.error('아이 기본 정보 입력 실패:', error);
    }
  };

  // ... 나머지 단계들

  return (
    <div>
      {currentStep === 1 && <GuardianInfoForm onSubmit={handleStep1} />}
      {currentStep === 2 && <ChildBasicInfoForm onSubmit={handleStep2} />}
      {/* ... 나머지 단계들 */}
    </div>
  );
};
```

### 사진 업로드 컴포넌트
```jsx
import React, { useState } from 'react';

const PhotoUpload = ({ userId }) => {
  const [photos, setPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (file) => {
    setUploading(true);
    try {
      const result = await uploadPhoto(userId, file, {
        type: 'profile',
        description: '프로필 사진',
        isPrimary: true
      });
      
      // 사진 목록 새로고침
      const updatedPhotos = await getUserPhotos(userId);
      setPhotos(updatedPhotos);
    } catch (error) {
      console.error('사진 업로드 실패:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        accept="image/*" 
        onChange={(e) => handleFileUpload(e.target.files[0])}
        disabled={uploading}
      />
      
      <div className="photo-gallery">
        {photos.map(photo => (
          <div key={photo.id}>
            <img 
              src={getPhotoUrl(userId, photo.filename)} 
              alt={photo.description}
            />
            <p>{photo.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 🌐 Axios를 사용한 예시

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 사용자 정보 입력
export const userAPI = {
  createGuardianInfo: (data) => api.post('/user-info/step1/', data),
  updateChildBasicInfo: (userId, data) => api.put(`/user-info/${userId}/step2/`, data),
  updateChildDetailInfo: (userId, data) => api.put(`/user-info/${userId}/step3/`, data),
  updateFrequentPlaces: (userId, data) => api.put(`/user-info/${userId}/step4/`, data),
  updateMissingInfo: (userId, data) => api.put(`/user-info/${userId}/step5/`, data),
  getUserProgress: (userId) => api.get(`/user-info/${userId}/progress/`),
  createCompleteUserInfo: (data) => api.post('/user-info/complete/', data),
};

// 사진 업로드
export const photoAPI = {
  uploadPhoto: (userId, formData) => api.post(`/photos/upload/${userId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getUserPhotos: (userId) => api.get(`/photos/user/${userId}`),
  updatePhoto: (photoId, data) => api.put(`/photos/${photoId}`, data),
  deletePhoto: (photoId) => api.delete(`/photos/${photoId}`),
  getPhotoUrl: (userId, filename) => `${API_BASE_URL}/photos/${userId}/${filename}`,
};
```

## 📱 모바일 앱 (React Native) 예시

```javascript
// React Native에서 파일 업로드
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

  try {
    const response = await fetch(`http://localhost:8000/photos/upload/${userId}`, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return await response.json();
  } catch (error) {
    console.error('업로드 실패:', error);
  }
};
```

## 🔒 CORS 설정 (필요시)

백엔드에서 CORS를 허용하려면:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 에러 처리

```javascript
const handleAPIError = (error) => {
  if (error.response) {
    // 서버 응답이 있는 경우
    console.error('API 에러:', error.response.data);
    return error.response.data;
  } else if (error.request) {
    // 요청은 보냈지만 응답이 없는 경우
    console.error('네트워크 에러:', error.request);
    return { detail: '서버에 연결할 수 없습니다.' };
  } else {
    // 요청 자체에 문제가 있는 경우
    console.error('요청 에러:', error.message);
    return { detail: '요청을 처리할 수 없습니다.' };
  }
};
```

## 🚀 배포 시 주의사항

1. **Base URL 변경**: 프로덕션 서버 URL로 변경
2. **HTTPS 사용**: 보안을 위해 HTTPS 필수
3. **CORS 설정**: 특정 도메인만 허용
4. **에러 처리**: 사용자 친화적인 에러 메시지
5. **로딩 상태**: 업로드 중 로딩 표시
6. **파일 크기 제한**: 프론트엔드에서도 파일 크기 체크

이 가이드를 참고하여 프론트엔드와 백엔드를 연동하세요! 🎯 