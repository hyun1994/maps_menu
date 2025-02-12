# 구글맵스 Embed API 사용하여 rating score로 지도필터링
# input으로 지역을 넣으면 스크립트 내에 ' 맛집' 기본값으로 설정하여 '지역 맛집'으로 검색
# rating score 4.6이상 기준으로 필터링 하지만 4.6이상이 없을 경우 4.3이상으로 처리
# 지도에 마커로 표기
# 마커 클릭하면 관련 요약정보 출력 or 카카오톡으로 관련 정보 전송
# 필요한 api : google maps / kakaotalk

import googlemaps
import folium
import requests

# 1. 구글맵스 API 키 설정
GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# 2. 카카오톡 API 설정
KAKAO_API_KEY = 'YOUR_KAKAO_API_KEY'
KAKAO_URL = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'

def search_restaurants(location, min_rating=4.6):
    # 3. 맛집 검색
    places = gmaps.places(query=f"{location} 맛집")
    filtered_results = []

    # 4. 결과 필터링 (rating score >= min_rating)
    for place in places['results']:
        if place.get('rating', 0) >= min_rating:
            filtered_results.append(place)
    return filtered_results

def create_map(locations):
    # 5. 지도 생성
    if not locations:
        print("검색된 맛집이 없습니다.")
        return None
    
    # 첫 번째 장소를 기준으로 지도 위치 설정
    first_location = locations[0].get('geometry', {}).get('location', {})
    
    if not first_location:
        print("위치 정보가 없어서 지도 생성을 할 수 없습니다.")
        return None
    
    lat, lng = first_location.get('lat'), first_location.get('lng')

    location_map = folium.Map(location=[lat, lng], zoom_start=12)

    for loc in locations:
        # 마커 추가 전, 'geometry'와 'location' 정보가 있는지 체크
        geometry = loc.get('geometry', {})
        location = geometry.get('location', {})
        
        if not location:
            continue
        
        lat = location.get('lat')
        lng = location.get('lng')
        name = loc.get('name', '이름 없음')
        rating = loc.get('rating', 'No rating')
        address = loc.get('formatted_address', '주소 없음')

        # 지도에 마커 추가
        folium.Marker(
            location=[lat, lng],
            popup=f"{name}<br><br>Rating: {rating}<br><br>{address}<br>",
            icon=folium.Icon(icon='cloud')
        ).add_to(location_map)

    return location_map

def send_to_kakao(message):
    headers = {
        'Authorization': f'Bearer {KAKAO_API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'template_object': {
            'object_type': 'text',
            'text': message,
            'link': {'web_url': 'https://your-restaurant-info.com'},
        }
    }
    
    response = requests.post(KAKAO_URL, headers=headers, json=data)
    return response.json()

# 6. 지역을 입력받고 맛집 검색
location = input("검색할 지역을 입력하세요: ")

# 7. 4.6 이상이 없을 경우 4.3 이상으로 처리
restaurants = search_restaurants(location, min_rating=4.6)
if not restaurants:
    print("4.6 이상 맛집이 없습니다. 4.3 이상으로 필터링합니다.")
    restaurants = search_restaurants(location, min_rating=4.3)

# 8. 지도에 마커 추가
map_output = create_map(restaurants)

# 9. 지도 HTML 파일로 저장
if map_output:
    map_output.save('restaurant_map.html')

# 10. 카카오톡으로 관련 정보를 전송
message = "추천 맛집 리스트: \n"
for restaurant in restaurants:
    message += f"{restaurant['name']}\n{restaurant.get('rating', 'No rating')}\n{restaurant['formatted_address']}"
send_to_kakao(message)

print("지도와 카카오톡 전송이 완료되었습니다.")