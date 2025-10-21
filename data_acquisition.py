import requests
import pandas as pd
import json
# from api_keys import GOOGLE_PLACES_API_KEY

latitude = 10.7769
longitude = 106.7009

radius = 3500  # in meters

overpass_url = "http://overpass-api.de/api/interpreter"


def build_overpass_query():
    query = f"""
    [out:json];
    (
      node(around:{radius},{latitude},{longitude})[amenity~'restaurant|cafe'];
    );
    out tags body;
    """
    return query

def fetch_osm_place():
    query = build_overpass_query()
    
    print(f'Đang gửi truy vấn Overpass tại vị trí ({latitude}, {longitude} (với bán kính: {radius}m)...')
    
    try:
        response = requests.post(overpass_url, data={'data': query})
        response.raise_for_status()
       
        results = response.json()
       
        restaurant_list = []
        for element in results['elements']:
           tags = element['tags']
           restaurant = {
               'OSM_ID': element['id'],
               'Name': tags.get('name', 'N/A'),
               'latitude': element['lat'],
               'longitude': element['lon'],
               'Amenity_Type': tags.get('amenity'),
               'Cuisine': tags.get('cuisine', 'N/A'),
               'Price_Level_OSM': tags.get('price', 'N/A'),
               'Website': tags.get('website', 'N/A'),
           }

           restaurant_list.append(restaurant)

        print(f'Thu thập thành công {len(restaurant_list)} địa điểm từ OSM.')
        return restaurant_list

    except requests.exceptions.RequestException as e:
        print(f'Đã xảy ra lỗi kết nối hoặc truy vấn thất bại: {e}')
        return []

def run_data_acquisition():
    osm_data = fetch_osm_place()
    df = pd.DataFrame(osm_data)
    
    output_file = 'restaurants_osm_data.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print('\n=================================================')
    print(f'Hoàn thành! Dữ liệu OSM đã được lưu vào file: {output_file}')
    print('=================================================')
    
if __name__ == "__main__":
    run_data_acquisition()