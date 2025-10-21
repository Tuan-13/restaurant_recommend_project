# # recommender.py

# import pandas as pd
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from geopy.distance import geodesic # Dùng cho Lọc Địa lý
# from basic_features import haversine_distance, normalize_rating
# import streamlit as st

# # Tên file dữ liệu đã xử lý từ nlp_processor.py
# PROCESSED_DATA_FILE = 'restaurants_processed_data.csv'

# # --- 1. TIỀN XỬ LÝ VÀ CHUẨN BỊ MÔ HÌNH ---
# @st.cache_data # Streamlit cache để tăng tốc độ tải dữ liệu
# def load_and_prepare_data():
#     """Đọc dữ liệu và tạo ma trận Cosine Similarity."""
    
#     df = pd.read_csv(PROCESSED_DATA_FILE)
    
#     # Chuẩn bị cột dữ liệu cho TF-IDF (Kết hợp Tên và Ẩm thực để phong phú hóa vector)
#     df['combined_features'] = df['Name'].fillna('') + ' ' + df['Cuisine'].fillna('')
    
#     # Khởi tạo và áp dụng TF-IDF
#     # TfidfVectorizer sẽ chuyển đổi văn bản thành ma trận vector số (đặc trưng)
#     tfidf = TfidfVectorizer(stop_words='english')
#     tfidf_matrix = tfidf.fit_transform(df['combined_features'])
    
#     # Tính toán Ma trận Độ tương đồng Cosine
#     cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
#     # Tạo chỉ mục ánh xạ tên nhà hàng với chỉ mục (index) DataFrame
#     indices = pd.Series(df.index, index=df['Name']).drop_duplicates()
    
#     return df, cosine_sim, indices

# # --- 2. LOGIC LỌC ĐỊA LÝ ---
# def filter_by_location(df, center_lat, center_lon, radius_km=3.5):
#     """Lọc các nhà hàng nằm trong bán kính 3.5km (RADIUS đã đặt trong data_acquisition.py)."""
    
#     center_location = (center_lat, center_lon)
    
#     # Tính khoảng cách từ nhà hàng đến vị trí trung tâm
#     def get_distance(row):
#         try:
#             restaurant_location = (row['Latitude'], row['Longitude'])
#             # Sử dụng công thức Haversine (geodesic)
#             return geodesic(center_location, restaurant_location).km
#         except:
#             return 9999 # Giá trị lớn nếu có lỗi
            
#     df['Distance_km'] = df.apply(get_distance, axis=1)
    
#     # Lọc những nhà hàng nằm trong bán kính cho phép
#     df_filtered = df[df['Distance_km'] <= radius_km].copy()
    
#     return df_filtered

# # --- 3. LOGIC GỢI Ý (Tính toán Điểm Cuối cùng) ---
# def find_best_restaurants(user_input_cuisine, user_budget_level, user_lat, user_lon, top_n=3):
#     """
#     Tìm nhà hàng tốt nhất dựa trên Tương đồng Ẩm thực, Xếp hạng Mô phỏng, và Lọc Ngân sách/Địa lý.
#     """
#     df, cosine_sim, indices = load_and_prepare_data()
    
#     # 3.1. Lọc Địa lý
#     df_filtered = filter_by_location(df, user_lat, user_lon)
#     if df_filtered.empty:
#         return pd.DataFrame() # Không tìm thấy nhà hàng nào gần đó

#     # Tạm thời gán một nhà hàng 'mô phỏng' làm điểm chuẩn cho độ tương đồng Ẩm thực.
#     # CHÚ Ý: Vì chúng ta không có lịch sử người dùng, ta sẽ tạo một vector ẩm thực TƯỞNG TƯỢNG:
#     temp_df = pd.DataFrame([{'Cuisine': user_input_cuisine, 'Name': 'TEMP_USER_PREF'}])
#     temp_df['combined_features'] = temp_df['Name'] + ' ' + temp_df['Cuisine']
    
#     # Thêm nhà hàng mô phỏng vào dữ liệu để tính vector đặc trưng
#     full_combined = pd.concat([df_filtered[['combined_features']], temp_df[['combined_features']]], ignore_index=True)
    
#     # Tạo lại ma trận TF-IDF cho tập dữ liệu đã lọc
#     tfidf = TfidfVectorizer(stop_words='english')
#     tfidf_matrix_filtered = tfidf.fit_transform(full_combined['combined_features'])
    
#     # Vector đặc trưng của người dùng (là dòng cuối cùng của ma trận)
#     user_vector = tfidf_matrix_filtered[-1] 
    
#     # Tính toán độ tương đồng Cosine giữa người dùng và TẤT CẢ nhà hàng đã lọc
#     cosine_scores = cosine_similarity(user_vector, tfidf_matrix_filtered[:-1])
    
#     # Chuyển điểm số thành Series để dễ dàng gán vào DataFrame
#     df_filtered['Cuisine_Similarity_Score'] = cosine_scores.flatten() 
    
#     # 3.2. Lọc Ngân sách (Chỉ áp dụng nếu Price_Level_OSM có giá trị)
#     # Price_Level_OSM: Giá trị số (1, 2, 3) hoặc 'N/A'
#     if user_budget_level > 0:
#         # Nếu OSM có giá trị, chỉ giữ lại những nhà hàng có mức giá phù hợp (<= ngân sách người dùng)
#         df_filtered = df_filtered[
#             (df_filtered['Price_Level_OSM'].astype(str) == 'N/A') |
#             (df_filtered['Price_Level_OSM'].fillna(0).astype(int) <= user_budget_level)
#         ]
        
#     # 3.3. TÍNH ĐIỂM XẾP HẠNG CUỐI CÙNG (FINAL RANKING SCORE)
#     # Điểm này là sự kết hợp giữa: Tương đồng Ẩm thực + Xếp hạng NLP
#     # Gán trọng số: 60% cho Tương đồng Ẩm thực và 40% cho Xếp hạng NLP (Final_NLP_Rating)
    
#     # Chuẩn hóa Final_NLP_Rating (điểm từ 1-5 sao) về thang [0, 1]
#     df_filtered['Norm_NLP_Rating'] = df_filtered['Final_NLP_Rating'] / 5.0
    
#     df_filtered['Final_Ranking_Score'] = (
#         0.6 * df_filtered['Cuisine_Similarity_Score'] + 
#         0.4 * df_filtered['Norm_NLP_Rating']
#     )
    
#     # Sắp xếp và lấy TOP N
#     recommendations = df_filtered.sort_values(by='Final_Ranking_Score', ascending=False).head(top_n)
    
#     return recommendations[['Name', 'Cuisine', 'Final_NLP_Rating', 'Distance_km']]


# if __name__ == '__main__':
#     # Ví dụ kiểm tra nếu chạy độc lập
#     # Tọa độ mô phỏng của người dùng
#     test_lat, test_lon = 21.03, 105.85 # Gần trung tâm Hà Nội
    
#     # Yêu cầu mô phỏng
#     test_cuisine = 'Vietnamese'
#     test_budget = 2 # Ngân sách trung bình
    
#     results = find_best_restaurants(test_cuisine, test_budget, test_lat, test_lon)
#     print("\nKết quả gợi ý:")
#     print(results)

# recommender.py

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from geopy.distance import geodesic
# from basic_features import normalize_rating # Dùng nếu muốn import hàm chuẩn hóa từ file tiện ích

# Tên file dữ liệu đã xử lý từ nlp_processor.py
PROCESSED_DATA_FILE = 'restaurants_processed_data.csv'
DEFAULT_RADIUS_KM = 3.5

# --- 1. TIỀN XỬ LÝ VÀ CHUẨN BỊ MÔ HÌNH ---

@st.cache_data 
def load_and_prepare_data():
    """Đọc dữ liệu và tiền xử lý các cột cần thiết."""
    
    try:
        df = pd.read_csv(PROCESSED_DATA_FILE)
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file dữ liệu: {PROCESSED_DATA_FILE}")
        return pd.DataFrame(), None, None

    # Chuẩn hóa cột Ẩm thực (đảm bảo chữ thường, không khoảng trắng dư thừa)
    df['Cuisine'] = df['Cuisine'].str.lower().str.strip().fillna('')

    # Tạo cột kết hợp cho TF-IDF: (Tên + Ẩm thực) để tạo vector đặc trưng phong phú hơn
    df['combined_features'] = df['Name'].fillna('') + ' ' + df['Cuisine']
    
    # Chuẩn hóa cột Mức giá OSM (nếu có)
    # Gán 0 cho các giá trị thiếu để dễ dàng lọc
    df['Price_Level_OSM'] = df['Price_Level_OSM'].fillna(0).astype(int)

    return df

# --- 2. LOGIC LỌC ĐỊA LÝ ---
def filter_by_location(df, center_lat, center_lon, radius_km=DEFAULT_RADIUS_KM):
    """Lọc các nhà hàng nằm trong bán kính cho phép."""
    
    if df.empty:
        return df
        
    center_location = (center_lat, center_lon)
    
    # Tính khoảng cách từ nhà hàng đến vị trí trung tâm
    def get_distance(row):
        try:
            restaurant_location = (row['Latitude'], row['Longitude'])
            # Sử dụng công thức geodesic (Haversine cải tiến) cho độ chính xác cao
            return geodesic(center_location, restaurant_location).km
        except:
            return 9999 # Giá trị lớn nếu có lỗi tọa độ
            
    df['Distance_km'] = df.apply(get_distance, axis=1)
    
    # Lọc những nhà hàng nằm trong bán kính cho phép
    df_filtered = df[df['Distance_km'] <= radius_km].copy()
    
    return df_filtered

# --- 3. LOGIC GỢI Ý (Tính toán Điểm Cuối cùng) ---
def find_best_restaurants(user_input_cuisine, user_budget_level, user_lat, user_lon, top_n=3):
    """
    Tìm nhà hàng tốt nhất dựa trên Tương đồng Ẩm thực, Xếp hạng NLP, và Lọc Ngân sách/Địa lý.
    """
    df = load_and_prepare_data()
    
    if df.empty:
        return pd.DataFrame()

    # 3.1. Lọc Địa lý
    df_filtered = filter_by_location(df, user_lat, user_lon)
    if df_filtered.empty:
        return pd.DataFrame() 

    # 3.2. Chuẩn bị Dữ liệu cho Tính toán Tương đồng
    # Tạo một vector đặc trưng cho yêu cầu của người dùng
    user_feature_string = f"TEMP_USER_PREF {user_input_cuisine.lower()}"
    
    # Thêm chuỗi đặc trưng của người dùng vào cuối DataFrame đã lọc
    full_combined = pd.concat([
        df_filtered[['combined_features']].rename(columns={'combined_features': 'feature'}), 
        pd.Series([user_feature_string], name='feature')
    ], ignore_index=True)

    # Tính TF-IDF và Cosine Similarity
    tfidf = TfidfVectorizer(stop_words='english')
    # Áp dụng TF-IDF cho tất cả nhà hàng đã lọc + chuỗi người dùng
    tfidf_matrix_filtered = tfidf.fit_transform(full_combined['feature'])
    
    # Vector đặc trưng của người dùng (dòng cuối cùng)
    user_vector = tfidf_matrix_filtered[-1] 
    
    # Tính toán độ tương đồng Cosine giữa người dùng và TẤT CẢ nhà hàng đã lọc
    # Ta chỉ cần tính vector của người dùng so với tất cả vector nhà hàng (trừ vector người dùng)
    cosine_scores = cosine_similarity(user_vector, tfidf_matrix_filtered[:-1])
    
    # Gán điểm tương đồng vào DataFrame
    df_filtered['Cuisine_Similarity_Score'] = cosine_scores.flatten() 
    
    # 3.3. Lọc Ngân sách
    # Chỉ giữ lại những nhà hàng có mức giá phù hợp (0 nghĩa là không có mức giá, vẫn được giữ lại)
    df_filtered = df_filtered[
        (df_filtered['Price_Level_OSM'] == 0) | 
        (df_filtered['Price_Level_OSM'] <= user_budget_level)
    ]
    
    # Nếu sau khi lọc ngân sách không còn nhà hàng nào
    if df_filtered.empty:
        return pd.DataFrame()

    # 3.4. TÍNH ĐIỂM XẾP HẠNG CUỐI CÙNG (FINAL RANKING SCORE)
    
    # Chuẩn hóa Final_NLP_Rating (điểm từ 1-5 sao) về thang [0, 1]
    # Nếu dùng basic_features: df_filtered['Norm_NLP_Rating'] = df_filtered['Final_NLP_Rating'].apply(normalize_rating)
    df_filtered['Norm_NLP_Rating'] = df_filtered['Final_NLP_Rating'].fillna(0) / 5.0
    
    # Áp dụng trọng số: 60% cho Tương đồng Ẩm thực (Lõi của gợi ý) và 40% cho Xếp hạng (Chất lượng)
    WEIGHT_SIMILARITY = 0.6
    WEIGHT_RATING = 0.4
    
    df_filtered['Final_Ranking_Score'] = (
        WEIGHT_SIMILARITY * df_filtered['Cuisine_Similarity_Score'] + 
        WEIGHT_RATING * df_filtered['Norm_NLP_Rating']
    )
    
    # Sắp xếp và lấy TOP N
    recommendations = df_filtered.sort_values(by='Final_Ranking_Score', ascending=False).head(top_n)
    
    # Trả về các cột cần hiển thị
    return recommendations[['Name', 'Cuisine', 'Final_NLP_Rating', 'Distance_km']]


if __name__ == '__main__':
    # Kiểm tra độc lập (không dùng Streamlit)
    print("Chạy kiểm tra mô hình gợi ý...")
    
    # Tọa độ mô phỏng của người dùng
    test_lat, test_lon = 21.03, 105.85 # Hà Nội
    
    # Yêu cầu mô phỏng
    test_cuisine = 'Vietnamese'
    test_budget = 2 # Ngân sách trung bình
    
    # Lưu ý: Hàm load_and_prepare_data() có sử dụng @st.cache_data, nhưng sẽ chạy bình thường 
    # trong môi trường non-streamlit lần đầu tiên.
    
    results = find_best_restaurants(test_cuisine, test_budget, test_lat, test_lon)
    
    if not results.empty:
        print(f"\n✅ Kết quả gợi ý (Top 3 cho {test_cuisine}, Ngân sách {test_budget}):")
        print(results.to_markdown(index=False, floatfmt=".2f"))
    else:
        print("\n❌ Không tìm thấy kết quả nào.")