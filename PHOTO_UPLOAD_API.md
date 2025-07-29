# 사진 업로드 API 문서

## 개요
실종아동 찾기 시스템에서 사진을 업로드하고 관리할 수 있는 API입니다.

## 기능
- 사진 업로드 (프로필, 실종 증거, 기타)
- 사진 목록 조회
- 사진 정보 수정
- 사진 삭제
- 사진 파일 서빙

## API 엔드포인트

### 1. 사진 업로드
```http
POST /photos/upload/{user_id}
```

**파라미터:**
- `user_id`: 사용자 ID (path parameter)

**폼 데이터:**
- `file`: 업로드할 이미지 파일 (필수)
- `image_type`: 이미지 타입 (필수) - "profile", "missing", "evidence"
- `description`: 사진 설명 (선택)
- `is_primary`: 대표 사진 여부 (기본값: false)

**응답:**
```json
{
  "photo_id": 1,
  "filename": "uuid-filename.jpg",
  "file_path": "uploads/1/uuid-filename.jpg",
  "file_size": 123456,
  "message": "사진이 성공적으로 업로드되었습니다."
}
```

### 2. 사용자 사진 목록 조회
```http
GET /photos/user/{user_id}
```

**응답:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "filename": "uuid-filename.jpg",
    "original_filename": "child_photo.jpg",
    "file_path": "uploads/1/uuid-filename.jpg",
    "file_size": 123456,
    "image_type": "profile",
    "description": "아이 프로필 사진",
    "width": 800,
    "height": 600,
    "mime_type": "image/jpeg",
    "is_active": true,
    "is_primary": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": null
  }
]
```

### 3. 사진 상세 조회
```http
GET /photos/{photo_id}
```

### 4. 사진 정보 수정
```http
PUT /photos/{photo_id}
```

**요청 본문:**
```json
{
  "image_type": "profile",
  "description": "수정된 사진 설명",
  "is_primary": true,
  "is_active": true
}
```

### 5. 사진 삭제
```http
DELETE /photos/{photo_id}
```

### 6. 사진 파일 접근
```http
GET /photos/{user_id}/{filename}
```

## 지원하는 파일 형식
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

## 파일 크기 제한
- 최대 10MB

## 이미지 타입
- `profile`: 프로필 사진
- `missing`: 실종 증거 사진
- `evidence`: 기타 증거 사진

## 사용 예시

### Python requests를 사용한 예시

```python
import requests

# 사진 업로드
with open('child_photo.jpg', 'rb') as f:
    files = {'file': ('child_photo.jpg', f, 'image/jpeg')}
    data = {
        'image_type': 'profile',
        'description': '아이 프로필 사진',
        'is_primary': True
    }
    
    response = requests.post(
        'http://localhost:8000/photos/upload/1',
        files=files,
        data=data
    )

# 사진 목록 조회
response = requests.get('http://localhost:8000/photos/user/1')
photos = response.json()

# 사진 파일 접근
photo_url = f"http://localhost:8000/photos/1/{photos[0]['filename']}"
```

### cURL을 사용한 예시

```bash
# 사진 업로드
curl -X POST "http://localhost:8000/photos/upload/1" \
  -F "file=@child_photo.jpg" \
  -F "image_type=profile" \
  -F "description=아이 프로필 사진" \
  -F "is_primary=true"

# 사진 목록 조회
curl "http://localhost:8000/photos/user/1"
```

## 오류 응답

### 파일 크기 초과
```json
{
  "detail": "파일 크기가 너무 큽니다. 최대 10MB까지 허용됩니다."
}
```

### 지원하지 않는 파일 타입
```json
{
  "detail": "지원하지 않는 파일 타입입니다. 지원 타입: image/jpeg, image/png, image/gif, image/webp"
}
```

### 사용자를 찾을 수 없음
```json
{
  "detail": "사용자를 찾을 수 없습니다"
}
```

## 파일 저장 구조
```
uploads/
├── 1/                    # 사용자 ID별 디렉토리
│   ├── uuid1.jpg
│   └── uuid2.png
├── 2/
│   └── uuid3.jpg
└── ...
```

## 보안 고려사항
1. 파일 확장자 검증
2. 파일 크기 제한
3. MIME 타입 검증
4. 고유한 파일명 생성 (UUID 사용)
5. 사용자별 디렉토리 분리

## 테스트
테스트 파일 `test_photo_upload.py`를 실행하여 모든 기능을 테스트할 수 있습니다:

```bash
python test_photo_upload.py
``` 