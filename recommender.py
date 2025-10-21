# recommender.py

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from geopy.distance import geodesic
import os # Thêm thư viện os để kiểm tra đường dẫn

# Tên file dữ liệu đã xử lý
PROCESSED_DATA_FILE = 'restaurants_processed_data.csv'
DEFAULT_RADIUS_KM = 3.5

# --- 1. TIỀN XỬ LÝ VÀ CHUẨN BỊ MÔ HÌNH ---

@st.cache_data 
def load_and_prepare_data():
    """Đọc dữ liệu và tiền xử lý các cột cần thiết."""
    
    # Gỡ bỏ đường dẫn tuyệt đối (nếu có) và chỉ dùng tên file
    current_dir = os.path.dirname(__file__) if os.path.dirname(__file__) else '.'
    file_path = os.path.join(current_dir, PROCESSED_DATA_FILE)

    try:
        if not os.path.exists(file_path):
             # Log đường dẫn đang tìm kiếm để dễ debug trên Cloud Log
            print(f"LỖI TẢI DỮ LIỆU: File không tồn tại tại {file_path}")
            # Thử lại từ thư mục gốc (áp dụng cho Streamlit Cloud)
            file_path = PROCESSED_DATA_FILE 
            print(f"Thử tải lại từ thư mục gốc: {file_path}")
            
        df = pd.read_csv(file_path) 
        print(f"TẢI DỮ LIỆU THÀNH CÔNG. Số hàng: {len(df)}")
        
    except FileNotFoundError as e:
        print(f"LỖI TẢI DỮ LIỆU CUỐI: Không thể tìm thấy file. Lỗi: {e}")
        return pd.DataFrame() 

    # Tiếp tục tiền xử lý
    df['Cuisine'] = df['Cuisine'].str.lower().str.strip().fillna('')
    df['combined_features'] = df['Name'].fillna('') + ' ' + df['Cuisine']
    df['Price_Level_OSM'] = df['Price_Level_OSM'].fillna(0).astype(int)

    return df

# --- 2. LOGIC LỌC ĐỊA LÝ ---
def filter_by_location(df, center_lat, center_lon, radius_km=DEFAULT_RADIUS_KM):
    """Lọc các nhà hàng nằm trong bán kính cho phép."""
    
    if df.empty:
        return df
        
    center_location = (center_lat, center_lon)
    
    def get_distance(row):
        try:
            restaurant_location = (row['Latitude'], row['Longitude'])
            return geodesic(center_location, restaurant_location).km
        except:
            return 9999
            
    df['Distance_km'] = df.apply(get_distance, axis=1)
    df_filtered = df[df['Distance_km'] <= radius_km].copy()
    
    return df_filtered

# --- 3. LOGIC GỢI Ý (Tính toán Điểm Cuối cùng) ---
def find_best_restaurants(user_input_cuisine, user_budget_level, user_lat, user_lon, top_n=3):
    """
    Tìm nhà hàng tốt nhất dựa trên Tương đồng Ẩm thực, Xếp hạng NLP, và Lọc Ngân sách/Địa lý.
    """
    df = load_and_prepare_data()
    
    if df.empty:
        # Quan trọng: Nếu dữ liệu rỗng, báo lỗi để Streamlit hiển thị 'Không tìm thấy'
        print("Dữ liệu rỗng, trả về DataFrame rỗng.")
        return pd.DataFrame()

    # 3.1. Lọc Địa lý
    df_filtered = filter_by_location(df, user_lat, user_lon)
    if df_filtered.empty:
        print("Không tìm thấy nhà hàng trong bán kính 3.5km.")
        return pd.DataFrame() 

    # 3.2. Tính toán Tương đồng Cosine
    user_feature_string = f"TEMP_USER_PREF {user_input_cuisine.lower()}"
    full_combined = pd.concat([
        df_filtered[['combined_features']].rename(columns={'combined_features': 'feature'}), 
        pd.Series([user_feature_string], name='feature')
    ], ignore_index=True)

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix_filtered = tfidf.fit_transform(full_combined['feature'])
    user_vector = tfidf_matrix_filtered[-1] 
    
    cosine_scores = cosine_similarity(user_vector, tfidf_matrix_filtered[:-1])
    df_filtered['Cuisine_Similarity_Score'] = cosine_scores.flatten() 
    
    # 3.3. Lọc Ngân sách
    if user_budget_level > 0:
        df_filtered = df_filtered[
            (df_filtered['Price_Level_OSM'] == 0) | 
            (df_filtered['Price_Level_OSM'] <= user_budget_level)
        ]
    
    if df_filtered.empty:
        print("Không tìm thấy nhà hàng phù hợp sau khi lọc ngân sách.")
        return pd.DataFrame()

    # 3.4. TÍNH ĐIỂM XẾP HẠNG CUỐI CÙNG
    df_filtered['Norm_NLP_Rating'] = df_filtered['Final_NLP_Rating'].fillna(0) / 5.0
    
    WEIGHT_SIMILARITY = 0.6
    WEIGHT_RATING = 0.4
    
    df_filtered['Final_Ranking_Score'] = (
        WEIGHT_SIMILARITY * df_filtered['Cuisine_Similarity_Score'] + 
        WEIGHT_RATING * df_filtered['Norm_NLP_Rating']
    )
    
    # Lấy TOP N
    recommendations = df_filtered.sort_values(by='Final_Ranking_Score', ascending=False).head(top_n)
    
    return recommendations[['Name', 'Cuisine', 'Final_NLP_Rating', 'Distance_km']]