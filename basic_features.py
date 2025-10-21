# basic_features.py

from math import radians, sin, cos, sqrt, atan2

# Bán kính Trái Đất theo km
R = 6371.0 

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách Haversine giữa hai cặp tọa độ (km).
    Đây là một công thức xấp xỉ, thường dùng trong các đồ án nhỏ.
    (Trong recommender.py bạn đã dùng geopy.distance.geodesic, mạnh mẽ hơn)
    
    Args:
        lat1, lon1: Vĩ độ và Kinh độ điểm 1.
        lat2, lon2: Vĩ độ và Kinh độ điểm 2.
    
    Returns:
        Khoảng cách tính bằng kilomet (km).
    """
    
    # Chuyển đổi từ độ sang radian
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Công thức Haversine
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def normalize_rating(rating, max_rating=5.0):
    """
    Chuẩn hóa điểm xếp hạng (rating) về phạm vi từ 0 đến 1.
    
    Args:
        rating: Điểm xếp hạng ban đầu (ví dụ: từ 1 đến 5).
        max_rating: Điểm xếp hạng tối đa.
        
    Returns:
        Điểm đã được chuẩn hóa (float từ 0.0 đến 1.0).
    """
    if max_rating == 0 or rating is None:
        return 0.0
    
    # Đảm bảo điểm không vượt quá max_rating
    return min(rating, max_rating) / max_rating

if __name__ == '__main__':
    # Kiểm tra hàm tính khoảng cách (Khoảng cách từ Hà Nội đến TP.HCM xấp xỉ 1120km)
    hn_lat, hn_lon = 21.0280, 105.8542
    hcm_lat, hcm_lon = 10.7797, 106.6991
    
    dist = haversine_distance(hn_lat, hn_lon, hcm_lat, hcm_lon)
    print(f"Khoảng cách Hà Nội - TP.HCM (Haversine): {dist:.2f} km")
    
    # Kiểm tra hàm chuẩn hóa
    test_rating = 4.2
    norm = normalize_rating(test_rating)
    print(f"Điểm {test_rating} được chuẩn hóa thành: {norm:.2f}")