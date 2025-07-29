from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "OK"} 

from pydantic import BaseModel

class HotzoneRequest(BaseModel):
    location_name: str
    child_age: int

@app.post("/api/hotzone")
def calculate_hotzone(req: HotzoneRequest):
    # TODO: get_location_coords, find_nearby_places, calculate_hotzone_score 호출
    return {"scored_places": []}

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
import folium
import osmnx as ox
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import warnings
from typing import List, Dict, Any

# 경고 무시
warnings.filterwarnings('ignore')

app = FastAPI()

# 1. 요청/응답 모델 정의
class HotzoneRequest(BaseModel):
    location_name: str
    child_age: int

class PlaceInfo(BaseModel):
    name: str
    place_type: str
    distance_km: float
    hotzone_score: float
    lat: float
    lon: float

class HotzoneResponse(BaseModel):
    scored_places: List[PlaceInfo]
    map_html: str
    center_coords: List[float]
    search_radius_km: float

# 2. 나이대별 설정 클래스
class AgeGroupConfig:
    def __init__(self, min_age, max_age, radius_km, tags, place_weights, fallback_tags=None):
        self.min_age = min_age
        self.max_age = max_age
        self.radius_km = radius_km
        self.tags = tags
        self.place_weights = place_weights
        self.fallback_tags = fallback_tags or {}  # 공백 해결을 위한 보조 태그

# 3. 수정된 나이대별 설정 정의
age_group_configs = [
    AgeGroupConfig(1, 4, 1,
                   tags={"leisure": ["playground", "park"], "amenity": ["kindergarten", "school"], "shop": ["convenience", "supermarket"]},
                   place_weights={
                       'playground': {'usage': 1.2, 'danger': 0.8},
                       'park': {'usage': 1.0, 'danger': 0.6},
                       'kindergarten': {'usage': 1.1, 'danger': 0.7},
                       'school': {'usage': 1.0, 'danger': 0.6},
                       'convenience': {'usage': 0.8, 'danger': 0.7},
                       'supermarket': {'usage': 0.7, 'danger': 0.7},
                       'default': {'usage': 0.5, 'danger': 0.5}
                   }),
    
    # 9-11세 설정 대폭 수정
    AgeGroupConfig(9, 11, 2.0,  # 반경을 3.2km에서 2.0km로 축소
                   tags={
                       "leisure": ["playground", "park", "sports_centre", "swimming_pool", "fitness_centre", "pitch", "tennis_court", "basketball_court"],
                       "amenity": ["school", "library", "community_centre", "fast_food", "restaurant", "cafe", "pharmacy", "hospital", "clinic", "bank", "post_office", "police", "fire_station"],
                       "shop": ["convenience", "supermarket", "bakery", "ice_cream", "toys", "books", "clothes", "department_store", "electronics", "sports", "music"],
                       "healthcare": ["pharmacy", "hospital", "clinic", "dentist"],
                       "tourism": ["attraction", "museum", "gallery", "cinema", "theatre"],
                       "building": ["public", "commercial", "retail", "school", "kindergarten"],
                       "landuse": ["residential", "commercial", "retail", "recreation_ground"]
                   },
                   place_weights={
                       # 교육 시설 (높은 가중치)
                       'school': {'usage': 1.4, 'danger': 0.2},      # 학교 - 매우 안전하고 유용
                       'kindergarten': {'usage': 1.3, 'danger': 0.2}, # 유치원 - 매우 안전
                       'library': {'usage': 1.2, 'danger': 0.2},     # 도서관 - 매우 안전하고 교육적
                       
                       # 놀이/운동 시설 (높은 가중치)
                       'playground': {'usage': 1.3, 'danger': 0.3},  # 놀이터 - 매우 유용
                       'park': {'usage': 1.2, 'danger': 0.3},        # 공원 - 안전하고 유용
                       'sports_centre': {'usage': 1.1, 'danger': 0.3}, # 체육관 - 운동에 좋음
                       'swimming_pool': {'usage': 1.0, 'danger': 0.4}, # 수영장 - 약간 위험하지만 유용
                       'fitness_centre': {'usage': 0.9, 'danger': 0.4}, # 피트니스센터
                       'pitch': {'usage': 1.0, 'danger': 0.3},       # 운동장
                       'tennis_court': {'usage': 0.9, 'danger': 0.3}, # 테니스장
                       'basketball_court': {'usage': 1.0, 'danger': 0.3}, # 농구장
                       
                       # 문화/여가 시설 (중간 가중치)
                       'museum': {'usage': 1.1, 'danger': 0.2},      # 박물관 - 교육적이고 안전
                       'gallery': {'usage': 0.9, 'danger': 0.3},     # 갤러리
                       'cinema': {'usage': 0.8, 'danger': 0.4},      # 영화관
                       'theatre': {'usage': 0.8, 'danger': 0.4},     # 극장
                       'attraction': {'usage': 0.9, 'danger': 0.4},  # 관광지
                       
                       # 상업 시설 (중간 가중치)
                       'convenience': {'usage': 0.9, 'danger': 0.5}, # 편의점 - 일상생활에 필요
                       'supermarket': {'usage': 0.8, 'danger': 0.5}, # 슈퍼마켓
                       'bakery': {'usage': 0.7, 'danger': 0.4},      # 베이커리
                       'ice_cream': {'usage': 0.8, 'danger': 0.4},   # 아이스크림점
                       'toys': {'usage': 0.9, 'danger': 0.3},        # 장난감점 - 아이들이 좋아함
                       'books': {'usage': 0.8, 'danger': 0.3},       # 서점 - 교육적
                       'clothes': {'usage': 0.6, 'danger': 0.5},     # 의류점
                       'department_store': {'usage': 0.7, 'danger': 0.6}, # 백화점
                       'electronics': {'usage': 0.6, 'danger': 0.5}, # 전자제품점
                       'sports': {'usage': 0.8, 'danger': 0.4},      # 스포츠용품점
                       'music': {'usage': 0.7, 'danger': 0.4},       # 음악점
                       
                       # 음식점 (중간 가중치)
                       'fast_food': {'usage': 0.7, 'danger': 0.6},   # 패스트푸드
                       'restaurant': {'usage': 0.7, 'danger': 0.6},  # 식당
                       'cafe': {'usage': 0.6, 'danger': 0.5},        # 카페
                       
                       # 의료 시설 (낮은 가중치)
                       'pharmacy': {'usage': 0.5, 'danger': 0.3},    # 약국 - 필요시에만
                       'hospital': {'usage': 0.6, 'danger': 0.5},    # 병원
                       'clinic': {'usage': 0.5, 'danger': 0.4},      # 진료소
                       'dentist': {'usage': 0.4, 'danger': 0.4},     # 치과
                       
                       # 공공 시설 (중간 가중치)
                       'community_centre': {'usage': 0.8, 'danger': 0.3}, # 주민센터
                       'bank': {'usage': 0.5, 'danger': 0.4},        # 은행
                       'post_office': {'usage': 0.6, 'danger': 0.3}, # 우체국
                       'police': {'usage': 0.7, 'danger': 0.2},      # 경찰서 - 안전
                       'fire_station': {'usage': 0.6, 'danger': 0.2}, # 소방서 - 안전
                       
                       # 건물/토지 유형 (낮은 가중치)
                       'public': {'usage': 0.7, 'danger': 0.4},      # 공공건물
                       'commercial': {'usage': 0.6, 'danger': 0.5},  # 상업건물
                       'retail': {'usage': 0.7, 'danger': 0.5},      # 소매상가
                       'residential': {'usage': 1.1, 'danger': 0.3}, # 주거지역 - 안전
                       'recreation_ground': {'usage': 1.0, 'danger': 0.3}, # 레크리에이션 공간
                       
                       'default': {'usage': 0.5, 'danger': 0.5}     # 기본값
                   },
                   # 공백 해결을 위한 보조 검색 태그
                   fallback_tags={
                       "building": ["school", "kindergarten", "public", "commercial", "retail", "residential"],
                       "landuse": ["residential", "commercial", "retail", "recreation_ground", "industrial"],
                       "highway": ["bus_stop", "pedestrian"],
                       "railway": ["station", "halt"],
                       "public_transport": ["station", "stop_position"]
                   }),
    
    # 다른 연령대는 기존 설정 유지...
    AgeGroupConfig(12, 14, 8,
                   tags={"leisure": ["park"], "amenity": ["school", "college", "university"], "shop": True},
                   place_weights={
                       'park': {'usage': 0.8, 'danger': 0.7},
                       'school': {'usage': 1.0, 'danger': 0.6},
                       'college': {'usage': 1.0, 'danger': 0.6},
                       'university': {'usage': 1.0, 'danger': 0.6},
                       'shop': {'usage': 1.0, 'danger': 0.7},
                       'default': {'usage': 0.7, 'danger': 0.6}
                   }),
                   
    AgeGroupConfig(15, 16, 23,
                   tags={"amenity": ["school", "college", "university", "bus_station"], "shop": True, "public_transport": True},
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

# 4. 개선된 핵심 함수들
def get_location_coords(location_name):
    """장소 이름을 입력받아 위도와 경도를 반환하는 함수"""
    try:
        geolocator = Nominatim(user_agent="hotzone-api")
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        print(f"지오코딩 중 오류 발생: {e}")
        return None

def find_nearby_places_enhanced(coords, radius_km, tags, fallback_tags=None):
    """향상된 주변 장소 검색 함수 - 공백 해결을 위한 다단계 검색"""
    try:
        # 1차 검색: 기본 태그로 검색
        print(f"1차 검색: 기본 태그로 반경 {radius_km}km 내 장소 검색...")
        gdf = ox.features_from_point(coords, tags, dist=radius_km * 1000)
        
        # 검색 결과가 부족한 경우 보조 검색 실행
        if len(gdf) < 10 and fallback_tags:
            print(f"검색 결과 부족 ({len(gdf)}개), 보조 태그로 추가 검색...")
            try:
                fallback_gdf = ox.features_from_point(coords, fallback_tags, dist=radius_km * 1000)
                if not fallback_gdf.empty:
                    # 기존 결과와 합치기
                    gdf = pd.concat([gdf, fallback_gdf], ignore_index=True)
                    print(f"보조 검색으로 {len(fallback_gdf)}개 추가 발견")
            except Exception as e:
                print(f"보조 검색 중 오류: {e}")
        
        # 여전히 결과가 부족한 경우 검색 반경 확대
        if len(gdf) < 5:
            extended_radius = min(radius_km * 1.5, 10)  # 최대 10km까지만 확대
            print(f"검색 결과 부족, 반경을 {extended_radius}km로 확대하여 재검색...")
            try:
                extended_gdf = ox.features_from_point(coords, tags, dist=extended_radius * 1000)
                if not extended_gdf.empty:
                    gdf = extended_gdf
                    print(f"확대 검색으로 {len(extended_gdf)}개 발견")
            except Exception as e:
                print(f"확대 검색 중 오류: {e}")
        
        print(f"최종 검색 결과: {len(gdf)}개 장소 발견")
        return gdf
        
    except Exception as e:
        print(f"주변 장소 검색 중 오류 발생: {e}")
        return pd.DataFrame()

def calculate_hotzone_score_enhanced(places_gdf, center_coords, age_config):
    """향상된 핫존 점수 계산 함수"""
    if places_gdf.empty:
        return places_gdf

    scores = []
    distances = []
    place_types = []
    
    place_weights = age_config.place_weights
    default_weights = place_weights.get('default', {'usage': 0.5, 'danger': 0.5})

    for idx, row in places_gdf.iterrows():
        if row.geometry is None:
            continue

        # 좌표 추출
        if not hasattr(row.geometry, 'centroid') or row.geometry.centroid is None:
            if hasattr(row.geometry, 'geoms') and len(row.geometry.geoms) > 0:
                place_coords = (row.geometry.geoms[0].centroid.y, row.geometry.geoms[0].centroid.x)
            else:
                continue
        else:
            place_coords = (row.geometry.centroid.y, row.geometry.centroid.x)

        distance = geodesic(center_coords, place_coords).km
        
        # 향상된 장소 유형 결정 로직
        current_place_type = determine_place_type_enhanced(row)
        
        weights = place_weights.get(current_place_type, default_weights)
        
        # 거리 기반 점수 계산 개선
        usage_score = weights['usage'] / (distance + 0.1)
        danger_score = weights['danger'] * (distance + 1)
        
        # 9-11세 특별 보너스 점수 (공백 해결을 위해)
        if age_config.min_age <= 9 <= age_config.max_age:
            if current_place_type in ['school', 'playground', 'park', 'library', 'museum', 'sports_centre', 'tennis_court', 'basketball_court']:
                usage_score *= 1.2  # 20% 보너스
        
        score = usage_score - danger_score

        scores.append(score)
        distances.append(distance)
        place_types.append(current_place_type)

    places_gdf['distance_km'] = distances
    places_gdf['place_type'] = place_types
    places_gdf['hotzone_score'] = scores

    return places_gdf.sort_values(by='hotzone_score', ascending=False)

def determine_place_type_enhanced(row):
    """향상된 장소 유형 결정 함수"""
    current_place_type = 'default'
    
    # 우선순위별 장소 유형 결정
    if 'amenity' in row and pd.notna(row['amenity']):
        amenity_type = row['amenity']
        if amenity_type in ['school', 'kindergarten', 'college', 'university']:
            current_place_type = 'school'
        elif amenity_type == 'library':
            current_place_type = 'library'
        elif amenity_type in ['fast_food', 'restaurant']:
            current_place_type = 'fast_food'
        elif amenity_type == 'cafe':
            current_place_type = 'cafe'
        elif amenity_type == 'community_centre':
            current_place_type = 'community_centre'
        elif amenity_type == 'pharmacy':
            current_place_type = 'pharmacy'
        elif amenity_type in ['hospital', 'clinic']:
            current_place_type = amenity_type
        elif amenity_type == 'bank':
            current_place_type = 'bank'
        elif amenity_type == 'post_office':
            current_place_type = 'post_office'
        elif amenity_type == 'police':
            current_place_type = 'police'
        elif amenity_type == 'fire_station':
            current_place_type = 'fire_station'

    if 'leisure' in row and pd.notna(row['leisure']):
        leisure_type = row['leisure']
        if leisure_type == 'playground':
            current_place_type = 'playground'
        elif leisure_type == 'park':
            current_place_type = 'park'
        elif leisure_type == 'sports_centre':
            current_place_type = 'sports_centre'
        elif leisure_type == 'swimming_pool':
            current_place_type = 'swimming_pool'
        elif leisure_type == 'fitness_centre':
            current_place_type = 'fitness_centre'
        elif leisure_type == 'pitch':
            current_place_type = 'pitch'
        elif leisure_type == 'tennis_court':
            current_place_type = 'tennis_court'
        elif leisure_type == 'basketball_court':
            current_place_type = 'basketball_court'

    if 'shop' in row and pd.notna(row['shop']):
        shop_type = row['shop']
        if shop_type == 'convenience':
            current_place_type = 'convenience'
        elif shop_type == 'supermarket':
            current_place_type = 'supermarket'
        elif shop_type in ['bakery', 'ice_cream', 'toys', 'books', 'clothes', 'electronics', 'sports', 'music']:
            current_place_type = shop_type
        elif shop_type == 'department_store':
            current_place_type = 'department_store'

    if 'healthcare' in row and pd.notna(row['healthcare']):
        healthcare_type = row['healthcare']
        if healthcare_type in ['pharmacy', 'hospital', 'clinic', 'dentist']:
            current_place_type = healthcare_type

    if 'tourism' in row and pd.notna(row['tourism']):
        tourism_type = row['tourism']
        if tourism_type in ['attraction', 'museum', 'gallery', 'cinema', 'theatre']:
            current_place_type = tourism_type

    # 건물 유형으로 보완
    if 'building' in row and pd.notna(row['building']) and current_place_type == 'default':
        building_type = row['building']
        if building_type in ['school', 'kindergarten']:
            current_place_type = 'school'
        elif building_type == 'public':
            current_place_type = 'public'
        elif building_type in ['commercial', 'retail']:
            current_place_type = building_type

    # 토지 이용으로 보완
    if 'landuse' in row and pd.notna(row['landuse']) and current_place_type == 'default':
        landuse_type = row['landuse']
        if landuse_type == 'residential':
            current_place_type = 'residential'
        elif landuse_type in ['commercial', 'retail']:
            current_place_type = landuse_type
        elif landuse_type == 'recreation_ground':
            current_place_type = 'recreation_ground'

    return current_place_type

# 기존 visualize_hotzone_map 함수는 그대로 유지...
def visualize_hotzone_map(scored_places, center_coords, location_name, radius_km):
    """점수가 매겨진 장소들을 지도에 시각화하는 함수"""
    if center_coords is None:
        return None

    # 지도 생성
    m = folium.Map(location=center_coords, zoom_start=14)

    # 실종 위치 마커
    folium.Marker(
        location=center_coords,
        popup=f"<b>실종 추정 위치</b><br>{location_name}",
        icon=folium.Icon(color='red', icon='user', prefix='fa')
    ).add_to(m)

    # 검색 반경 표시
    folium.Circle(
        location=center_coords,
        radius=radius_km * 1000,
        color='#3186cc',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.1
    ).add_to(m)

    if scored_places.empty:
        return m

    # 점수 정규화 및 색상 매핑
    scores = scored_places['hotzone_score']
    min_score, max_score = scores.min(), scores.max()

    if max_score == min_score:
        normalized_scores = pd.Series([0.5] * len(scores), index=scores.index)
    else:
        normalized_scores = (scores - min_score) / (max_score - min_score)

    cmap = plt.get_cmap('hot_r')

    # 각 장소를 지도에 마커로 추가
    for idx, row in scored_places.iterrows():
        if row.geometry is None:
            continue

        if not hasattr(row.geometry, 'centroid') or row.geometry.centroid is None:
            if hasattr(row.geometry, 'geoms') and len(row.geometry.geoms) > 0:
                coords = (row.geometry.geoms[0].centroid.y, row.geometry.geoms[0].centroid.x)
            else:
                continue
        else:
            coords = (row.geometry.centroid.y, row.geometry.centroid.x)

        score = row['hotzone_score']
        
        if max_score == min_score:
            norm_score = 0.5
        else:
            norm_score = (score - min_score) / (max_score - min_score)

        color_hex = cmap(norm_score)
        color_hex_str = f"#{int(color_hex[0]*255):02x}{int(color_hex[1]*255):02x}{int(color_hex[2]*255):02x}"

        popup_html = f"""
        <b>{row['name'] if 'name' in row and pd.notna(row['name']) else '이름 없음'}</b><br>
        유형: {row['place_type']}<br>
        거리: {row['distance_km']:.2f} km<br>
        <b>핫존 점수: {row['hotzone_score']:.2f}</b>
        """

        folium.CircleMarker(
            location=coords,
            radius=8,
            color=color_hex_str,
            fill=True,
            fill_color=color_hex_str,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)

    return m

# 5. API 엔드포인트들
@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.post("/api/hotzone", response_model=HotzoneResponse)
def calculate_hotzone_api(req: HotzoneRequest):
    try:
        # 1. 좌표 변환
        center_coords = get_location_coords(req.location_name)
        if center_coords is None:
            raise HTTPException(status_code=404, detail="해당 위치를 찾을 수 없습니다.")

        # 2. 나이대별 설정 찾기
        selected_config = None
        for config in age_group_configs:
            if config.min_age <= req.child_age <= config.max_age:
                selected_config = config
                break

        if selected_config is None:
            selected_config = age_group_configs[-1]

        # 3. 향상된 주변 장소 검색
        nearby_places = find_nearby_places_enhanced(
            center_coords, 
            selected_config.radius_km, 
            selected_config.tags,
            selected_config.fallback_tags
        )
        
        if nearby_places.empty:
            return HotzoneResponse(
                scored_places=[],
                map_html="<div>주변 장소를 찾을 수 없습니다.</div>",
                center_coords=list(center_coords),
                search_radius_km=selected_config.radius_km
            )

        # 4. 향상된 핫존 점수 계산
        scored_places = calculate_hotzone_score_enhanced(nearby_places, center_coords, selected_config)
        
        # 상위 100개로 확대 (기존 50개에서)
        top_places = scored_places.head(100)

        # 5. 지도 생성
        hotzone_map = visualize_hotzone_map(top_places, center_coords, req.location_name, selected_config.radius_km)
        map_html = hotzone_map._repr_html_() if hotzone_map else "<div>지도 생성 실패</div>"

        # 6. JSON 직렬화 가능한 형태로 변환
        place_list = []
        for idx, row in top_places.iterrows():
            if row.geometry is None:
                continue
                
            # 좌표 추출
            if not hasattr(row.geometry, 'centroid') or row.geometry.centroid is None:
                if hasattr(row.geometry, 'geoms') and len(row.geometry.geoms) > 0:
                    coords = (row.geometry.geoms[0].centroid.y, row.geometry.geoms[0].centroid.x)
                else:
                    continue
            else:
                coords = (row.geometry.centroid.y, row.geometry.centroid.x)

            place_info = PlaceInfo(
                name=row['name'] if 'name' in row and pd.notna(row['name']) else '이름 없음',
                place_type=row['place_type'],
                distance_km=round(row['distance_km'], 2),
                hotzone_score=round(row['hotzone_score'], 2),
                lat=coords[0],
                lon=coords[1]
            )
            place_list.append(place_info)

        return HotzoneResponse(
            scored_places=place_list,
            map_html=map_html,
            center_coords=list(center_coords),
            search_radius_km=selected_config.radius_km
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 지도만 표시하는 엔드포인트 추가
@app.get("/map/{location_name}/{child_age}", response_class=HTMLResponse)
def show_hotzone_map(location_name: str, child_age: int):
    try:
        center_coords = get_location_coords(location_name)
        if center_coords is None:
            return HTMLResponse("<h1>해당 위치를 찾을 수 없습니다.</h1>")

        selected_config = None
        for config in age_group_configs:
            if config.min_age <= child_age <= config.max_age:
                selected_config = config
                break
        
        if selected_config is None:
            selected_config = age_group_configs[-1]

        nearby_places = find_nearby_places_enhanced(
            center_coords, 
            selected_config.radius_km, 
            selected_config.tags,
            selected_config.fallback_tags
        )
        
        if nearby_places.empty:
            m = folium.Map(location=center_coords, zoom_start=14)
            folium.Marker(
                location=center_coords,
                popup=f"<b>실종 추정 위치</b><br>{location_name}",
                icon=folium.Icon(color='red', icon='user', prefix='fa')
            ).add_to(m)
            return HTMLResponse(m.get_root().render())

        scored_places = calculate_hotzone_score_enhanced(nearby_places, center_coords, selected_config)
        top_places = scored_places.head(100)

        hotzone_map = visualize_hotzone_map(top_places, center_coords, location_name, selected_config.radius_km)
        
        return HTMLResponse(hotzone_map.get_root().render())

    except Exception as e:
        return HTMLResponse(f"<h1>오류 발생</h1><p>{str(e)}</p>")
