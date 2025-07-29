#!/usr/bin/env python3
"""
API 테스트 스크립트
팀원들이 API가 어떻게 작동하는지 확인할 수 있는 테스트 코드
"""

import requests
import json

# API 기본 URL
BASE_URL = "http://localhost:8000"

def test_basic_endpoints():
    """기본 엔드포인트 테스트"""
    print("=== 기본 엔드포인트 테스트 ===")
    
    # 루트 엔드포인트
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ 루트 엔드포인트: {response.json()}")
    except Exception as e:
        print(f"❌ 루트 엔드포인트 오류: {e}")

def test_emergency_contacts():
    """긴급 연락처 테스트"""
    print("\n=== 긴급 연락처 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/emergency-contacts/")
        contacts = response.json()
        print(f"✅ 긴급 연락처 {len(contacts)}개 조회:")
        for contact in contacts:
            print(f"  - {contact['name']}: {contact['phone_number']}")
    except Exception as e:
        print(f"❌ 긴급 연락처 조회 오류: {e}")

def test_notices():
    """공지사항 테스트"""
    print("\n=== 공지사항 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/notices/")
        notices = response.json()
        print(f"✅ 공지사항 {len(notices)}개 조회:")
        for notice in notices:
            print(f"  - {notice['title']}: {notice['content'][:50]}...")
    except Exception as e:
        print(f"❌ 공지사항 조회 오류: {e}")

def test_user_creation():
    """사용자 생성 테스트"""
    print("\n=== 사용자 생성 테스트 ===")
    
    user_data = {
        "guardian_name": "김보호",
        "guardian_phone": "010-1234-5678",
        "child_name": "김아이",
        "child_gender": "남",
        "child_birth_date": "2018-05-15",
        "child_characteristics": "검은 머리, 큰 눈",
        "child_height": 120.5,
        "child_weight": 25.0,
        "child_clothing": "파란색 티셔츠, 검은 바지"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ 사용자 생성 성공: ID {user['id']}")
            return user['id']
        else:
            print(f"❌ 사용자 생성 실패: {response.text}")
    except Exception as e:
        print(f"❌ 사용자 생성 오류: {e}")
    
    return None

def test_hotzone_creation(user_id):
    """핫존 생성 테스트"""
    if not user_id:
        print("❌ 사용자 ID가 없어 핫존 생성 테스트를 건너뜁니다.")
        return
    
    print("\n=== 핫존 생성 테스트 ===")
    
    hotzone_data = {
        "user_id": user_id,
        "missing_location": "서울특별시 강남구 역삼동",
        "child_age": 7,
        "radius_km": 1.5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/hotzones/create/", json=hotzone_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 핫존 생성 성공:")
            print(f"  - 실종아동 ID: {result['missing_child_id']}")
            print(f"  - 핫존 개수: {result['total_count']}개")
            print(f"  - 검색 반경: {result['search_radius']}km")
            
            # 핫존 목록 조회
            hotzones_response = requests.get(f"{BASE_URL}/hotzones/{result['missing_child_id']}")
            if hotzones_response.status_code == 200:
                hotzones = hotzones_response.json()
                print(f"  - 상위 3개 핫존:")
                for i, hotzone in enumerate(hotzones[:3]):
                    print(f"    {i+1}. {hotzone['place_name']} (점수: {hotzone['hotzone_score']:.2f})")
        else:
            print(f"❌ 핫존 생성 실패: {response.text}")
    except Exception as e:
        print(f"❌ 핫존 생성 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 실종아동 찾기 백엔드 API 테스트")
    print("=" * 50)
    
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ 서버가 실행 중입니다.")
    except:
        print("❌ 서버가 실행되지 않았습니다.")
        print("다음 명령어로 서버를 실행하세요:")
        print("python main.py")
        return
    
    # 테스트 실행
    test_basic_endpoints()
    test_emergency_contacts()
    test_notices()
    user_id = test_user_creation()
    test_hotzone_creation(user_id)
    
    print("\n" + "=" * 50)
    print("🎉 테스트 완료!")

if __name__ == "__main__":
    main()
