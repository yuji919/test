import pandas as pd
import osmnx as ox
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import warnings
from typing import List, Dict, Any
from app.models.models import Hotzone, MissingChild, User
from app.database.database import SessionLocal
from sqlalchemy.orm import Session

warnings.filterwarnings('ignore')

class AgeGroupConfig:
    """나이대별 설정 클래스"""
    def __init__(self, min_age: int, max_age: int, radius_km: float, tags: Dict, place_weights: Dict):
        self.min_age = min_age
        self.max_age = max_age
        self.radius_km = radius_km
        self.tags = tags
        self.place_weights = place_weights

# 나이대별 설정 정의
AGE_GROUP_CONFIGS = [
    AgeGroupConfig(1, 4, 1.0,
                   tags={"leisure": ["playground", "park"], "amenity": ["kindergarten", "school"], "shop": ["kids_cafe"]},
                   place_weights={
                       'playground': {'usage': 1.2, 'danger': 0.8},
                       'park': {'usage': 1.0, 'danger': 0.6},
                       'kindergarten': {'usage': 1.1, 'danger': 0.7},
                       'school': {'usage': 1.0, 'danger': 0.6},
                       'kids_cafe': {'usage': 1.0, 'danger': 0.7},
                       'default': {'usage': 0.5, 'danger': 0.5}
                   }),
    AgeGroupConfig(5, 8, 1.3,
                   tags={"leisure": ["playground", "park"], "amenity": ["kindergarten", "school", "residential"]},
                   place_weights={
                       'residential': {'usage': 1.0, 'danger': 0.5},
                       'playground': {'usage': 1.1, 'danger': 0.7},
                       'park': {'usage': 0.9, 'danger': 0.5},
                       'kindergarten': {'usage': 1.0, 'danger': 0.6},
                       'school': {'usage': 1.2, 'danger': 0.4},
                       'default': {'usage': 0.5, 'danger': 0.5}
                   }),
    AgeGroupConfig(9, 11, 3.2,
                   tags={"leisure": ["playground", "park"], "amenity": ["school", "residential"]},
                   place_weights={
                       'playground': {'usage': 0.9, 'danger': 0.4},
                       'park': {'usage': 1.1, 'danger': 0.5},
                       'school': {'usage': 1.1, 'danger': 0.4},
                       'residential': {'usage': 1.2, 'danger': 0.5},
                       'default': {'usage': 0.6, 'danger': 0.4}
                   }),
    AgeGroupConfig(12, 14, 8.0,
                   tags={"leisure": ["park"], "amenity": ["school", "college", "university"], "shop": True},
                   place_weights={
                       'park': {'usage': 0.8, 'danger': 0.7},
                       'school': {'usage': 1.0, 'danger': 0.6},
                       'college': {'usage': 1.0, 'danger': 0.6},
                       'university': {'usage': 1.0, 'danger': 0.6},
                       'shop': {'usage': 1.0, 'danger': 0.7},
                       'default': {'usage': 0.7, 'danger': 0.6}
                   }),
    AgeGroupConfig(15, 16, 23.0,
                   tags={"amenity": ["school", "college", "university", "bus_station", "railway_station"], "shop": True},
                   place_weights={
                       'school': {'usage': 0.6, 'danger': 0.8},
                       'college': {'usage': 0.6, 'danger': 0.8},
                       'university': {'usage': 0.6, 'danger': 0.8},
                       'shop': {'usage': 1.2, 'danger': 0.6},
                       'bus_stop': {'usage': 1.2, 'danger': 0.6},
                       'subway_station': {'usage': 1.2, 'danger': 0.6},
                       'default': {'usage': 0.8, 'danger': 0.7}
                   }),
]

class HotzoneService:
    """핫존 생성 서비스"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="missing-children-hotzone-finder")
    
    def get_location_coords(self, location_name: str) -> tuple:
        """장소 이름을 입력받아 위도와 경도를 반환"""
        try:
            location = self.geolocator.geocode(location_name)
            if location:
                return (location.latitude, location.longitude)
            return None
        except Exception as e:
            print(f"지오코딩 중 오류 발생: {e}")
            return None
    
    def find_nearby_places(self, coords: tuple, radius_km: float, tags: Dict) -> pd.DataFrame:
        """중심 좌표, 반경, 태그를 기반으로 주변 장소를 검색"""
        try:
            gdf = ox.features_from_point(coords, tags, dist=radius_km * 1000)
            return gdf
        except Exception as e:
            print(f"주변 장소 검색 중 오류 발생: {e}")
            return pd.DataFrame()
    
    def calculate_hotzone_score(self, places_gdf: pd.DataFrame, center_coords: tuple, age_config: AgeGroupConfig) -> pd.DataFrame:
        """장소 목록과 중심 좌표를 받아 '핫존 점수'를 계산"""
        if places_gdf.empty:
            return places_gdf
        
        scores = []
        distances = []
        place_types = []
        usage_weights = []
        danger_weights = []
        
        place_weights = age_config.place_weights
        default_weights = place_weights.get('default', {'usage': 0.5, 'danger': 0.5})
        
        for idx, row in places_gdf.iterrows():
            if row.geometry is None:
                continue
            
            if not hasattr(row.geometry, 'centroid') or row.geometry.centroid is None:
                if hasattr(row.geometry, 'geoms') and len(row.geometry.geoms) > 0:
                    place_coords = (row.geometry.geoms[0].centroid.y, row.geometry.geoms[0].centroid.x)
                else:
                    continue
            else:
                place_coords = (row.geometry.centroid.y, row.geometry.centroid.x)
            
            distance = geodesic(center_coords, place_coords).km
            
            # 장소 유형 결정
            current_place_type = 'default'
            
            if 'amenity' in row and pd.notna(row['amenity']):
                if row['amenity'] in ['school', 'kindergarten', 'college', 'university']:
                    current_place_type = 'school'
                elif row['amenity'] == 'residential':
                    current_place_type = 'residential'
                elif row['amenity'] == 'bus_station':
                    current_place_type = 'bus_stop'
            
            if 'leisure' in row and pd.notna(row['leisure']):
                if row['leisure'] == 'playground':
                    current_place_type = 'playground'
                elif row['leisure'] == 'park':
                    current_place_type = 'park'
            
            if 'shop' in row and pd.notna(row['shop']) and row['shop'] in ['convenience', 'supermarket']:
                current_place_type = 'shop'
            
            if 'railway' in row and pd.notna(row['railway']) and row['railway'] == 'station':
                current_place_type = 'subway_station'
            
            if 'name' in row and isinstance(row['name'], str) and '키즈카페' in row['name']:
                current_place_type = 'kids_cafe'
            
            weights = place_weights.get(current_place_type, default_weights)
            
            usage_score = weights['usage'] / (distance + 0.1)
            danger_score = weights['danger'] * (distance + 1)
            score = usage_score - danger_score
            
            scores.append(score)
            distances.append(distance)
            place_types.append(current_place_type)
            usage_weights.append(weights['usage'])
            danger_weights.append(weights['danger'])
        
        places_gdf['distance_km'] = distances
        places_gdf['place_type'] = place_types
        places_gdf['hotzone_score'] = scores
        places_gdf['usage_weight'] = usage_weights
        places_gdf['danger_weight'] = danger_weights
        
        return places_gdf.sort_values(by='hotzone_score', ascending=False)
    
    def create_hotzones(self, user_id: int, missing_location: str, child_age: int, radius_km: float = None) -> Dict[str, Any]:
        """핫존 생성 메인 함수"""
        # 사용자 정보 조회
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "사용자를 찾을 수 없습니다."}
            
            # 실종 위치 좌표 가져오기
            center_coords = self.get_location_coords(missing_location)
            if not center_coords:
                return {"error": "실종 위치를 찾을 수 없습니다."}
            
            # 나이대별 설정 찾기
            selected_config = None
            for config in AGE_GROUP_CONFIGS:
                if config.min_age <= child_age <= config.max_age:
                    selected_config = config
                    break
            
            if not selected_config:
                selected_config = AGE_GROUP_CONFIGS[-1]  # 기본 설정 사용
            
            # 반경 설정
            search_radius = radius_km if radius_km else selected_config.radius_km
            
            # 주변 장소 검색
            nearby_places = self.find_nearby_places(center_coords, search_radius, selected_config.tags)
            
            if nearby_places.empty:
                return {"error": "주변 장소를 찾을 수 없습니다."}
            
            # 핫존 점수 계산
            scored_places = self.calculate_hotzone_score(nearby_places, center_coords, selected_config)
            
            # 상위 50개만 선택
            top_places = scored_places.head(50)
            
            # 실종아동 정보 생성
            missing_child = MissingChild(
                user_id=user_id,
                missing_date=pd.Timestamp.now(),
                missing_location=missing_location,
                missing_latitude=center_coords[0],
                missing_longitude=center_coords[1],
                child_age=child_age
            )
            db.add(missing_child)
            db.flush()  # ID 생성
            
            # 핫존 정보 저장
            hotzones = []
            for idx, row in top_places.iterrows():
                if row.geometry is None:
                    continue
                
                if not hasattr(row.geometry, 'centroid') or row.geometry.centroid is None:
                    if hasattr(row.geometry, 'geoms') and len(row.geometry.geoms) > 0:
                        coords = (row.geometry.geoms[0].centroid.y, row.geometry.geoms[0].centroid.x)
                    else:
                        continue
                else:
                    coords = (row.geometry.centroid.y, row.geometry.centroid.x)
                
                hotzone = Hotzone(
                    missing_child_id=missing_child.id,
                    place_name=row.get('name', '이름 없음'),
                    place_type=row['place_type'],
                    place_address=row.get('addr:full', ''),
                    latitude=coords[0],
                    longitude=coords[1],
                    distance_km=row['distance_km'],
                    hotzone_score=row['hotzone_score'],
                    usage_weight=row['usage_weight'],
                    danger_weight=row['danger_weight']
                )
                db.add(hotzone)
                hotzones.append(hotzone)
            
            db.commit()
            
            return {
                "missing_child_id": missing_child.id,
                "hotzones": hotzones,
                "total_count": len(hotzones),
                "search_radius": search_radius
            }
            
        except Exception as e:
            db.rollback()
            return {"error": f"핫존 생성 중 오류 발생: {str(e)}"}
        finally:
            db.close()
