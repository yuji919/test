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
from typing import List

# 경고 무시
warnings.filterwarnings('ignore')

app = FastAPI(
    title="Hotzone Backend API",
    description="아동 실종 시 핫존(가능성이 높은 지역)을 분석하는 API",
    version="1.0.0"
)

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
    def __init__(self, min_age, max_age, radius_km, tags, place_weights):
        self.min_age = min_age
        self.max_age = max_age
        self.radius_km = radius_km
        self.tags = tags
        self.place_weights = place_weights

# 3. 나이대별 설정 정의
age_group_configs = [
    AgeGroupConfig(1, 4, 1,
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

# 4. 핵심 함수들
def get_location_coords(location_name: str):
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

def find_nearby_places(coords, radius_km, tags):
    """중심 좌표, 반경, 태그를 기반으로 주변 장소를 검색하는 함수"""
    try:
        gdf = ox.features_from_point(coords, tags, dist=radius_km * 1000)
        return gdf
    except Exception as e:
        print(f"주변 장소 검색 중 오류 발생: {e}")
        return pd.DataFrame()

def calculate_hotzone_score(places_gdf, center_coords, age_config):
    """장소 목록과 중심 좌표를 받아 핫존 점수를 계산하는 함수"""
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

        if 'shop' in row and pd.notna(row['shop']):
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

    places_gdf['distance_km'] = distances
    places_gdf['place_type'] = place_types
    places_gdf['hotzone_score'] = scores

    return places_gdf.sort_values(by='hotzone_score', ascending=False)

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
    """서버 상태 확인"""
    return {"status": "OK"}

@app.post("/api/hotzone", response_model=HotzoneResponse)
def calculate_hotzone_api(req: HotzoneRequest):
    """핫존 분석 API - JSON 응답"""
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
            # 기본값으로 가장 넓은 반경 사용
            selected_config = age_group_configs[-1]

        # 3. 주변 장소 검색
        nearby_places = find_nearby_places(center_coords, selected_config.radius_km, selected_config.tags)
        
        if nearby_places.empty:
            # 빈 결과 반환
            return HotzoneResponse(
                scored_places=[],
                map_html="<div>주변 장소를 찾을 수 없습니다.</div>",
                center_coords=list(center_coords),
                search_radius_km=selected_config.radius_km
            )

        # 4. 핫존 점수 계산
        scored_places = calculate_hotzone_score(nearby_places, center_coords, selected_config)
        
        # 상위 50개만 선택
        top_places = scored_places.head(50)

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

@app.get("/map/{location_name}/{child_age}", response_class=HTMLResponse)
def show_hotzone_map(location_name: str, child_age: int):
    """핫존 지도 뷰 - HTML 응답"""
    try:
        # 1. 좌표 변환
        center_coords = get_location_coords(location_name)
        if center_coords is None:
            return HTMLResponse("<h1>해당 위치를 찾을 수 없습니다.</h1>")

        # 2. 나이대별 설정 찾기
        selected_config = None
        for config in age_group_configs:
            if config.min_age <= child_age <= config.max_age:
                selected_config = config
                break
        
        if selected_config is None:
            selected_config = age_group_configs[-1]

        # 3. 주변 장소 검색 및 점수 계산
        nearby_places = find_nearby_places(center_coords, selected_config.radius_km, selected_config.tags)
        
        if nearby_places.empty:
            # 빈 지도라도 표시
            m = folium.Map(location=center_coords, zoom_start=14)
            folium.Marker(
                location=center_coords,
                popup=f"<b>실종 추정 위치</b><br>{location_name}",
                icon=folium.Icon(color='red', icon='user', prefix='fa')
            ).add_to(m)
            return HTMLResponse(m.get_root().render())

        scored_places = calculate_hotzone_score(nearby_places, center_coords, selected_config)
        top_places = scored_places.head(50)

        # 4. 지도 생성
        hotzone_map = visualize_hotzone_map(top_places, center_coords, location_name, selected_config.radius_km)
        
        # 5. HTML로 반환
        return HTMLResponse(hotzone_map.get_root().render())

    except Exception as e:
        return HTMLResponse(f"<h1>오류 발생</h1><p>{str(e)}</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
