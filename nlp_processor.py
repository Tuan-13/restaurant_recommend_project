# nlp_processor.py - Mã xử lý để tạo ra restaurants_processed_data.csv

import pandas as pd
import random 
import os
import time

# --- CẤU HÌNH FILE DỮ LIỆU ---
# Đổi tên file này nếu file dữ liệu thô của bạn khác
RAW_DATA_FILE = 'restaurants_osm_data.csv' 
OUTPUT_FILE = 'restaurants_processed_data.csv'

# --- LOGIC XỬ LÝ DỮ LIỆU ---
def process_data_pipeline():
    
    print(f"Bắt đầu quá trình xử lý dữ liệu. Đang tìm file thô: {RAW_DATA_FILE}")

    # 1. Tải Dữ liệu Thô
    try:
        # Giả định file thô có các cột cơ bản như 'Name', 'Cuisine'
        df = pd.read_csv(RAW_DATA_FILE, encoding='utf-8')
        print(f"Tải dữ liệu thô thành công. Tổng số hàng: {len(df)}")
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file dữ liệu thô: {RAW_DATA_FILE}.")
        print("Vui lòng đảm bảo file này tồn tại và chứa dữ liệu nhà hàng.")
        return
    except Exception as e:
        print(f"LỖI TẢI DỮ LIỆU THÔ: {e}")
        return

    # 2. Bổ sung Tọa độ (Latitude/Longitude)
    # LƯU Ý: Nếu bạn có cột tọa độ thực tế, hãy bỏ qua đoạn code tạo ngẫu nhiên này.
    print("Bước 1: Bổ sung Tọa độ (Giả định gần Hà Nội)...")
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        
        # Tạo tọa độ ngẫu nhiên gần trung tâm Hà Nội (21.0, 105.8)
        # Phạm vi khoảng 10km quanh trung tâm
        df['Latitude'] = [21.02 + random.uniform(-0.05, 0.05) for _ in range(len(df))]
        df['Longitude'] = [105.85 + random.uniform(-0.05, 0.05) for _ in range(len(df))]
        
        print("Đã tạo Tọa độ ngẫu nhiên cho tất cả các hàng.")
    else:
        print("Sử dụng các cột Tọa độ hiện có.")
    
    # Đảm bảo chúng là kiểu số
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    # 3. Xử lý NLP và Tạo Final_NLP_Rating (Giả lập)
    print("Bước 2: Tạo Xếp hạng NLP mô phỏng (3.0 đến 5.0)...")
    if 'Final_NLP_Rating' not in df.columns:
        # Tạo điểm xếp hạng mô phỏng
        df['Final_NLP_Rating'] = [random.uniform(3.0, 5.0) for _ in range(len(df))]
    else:
        print("Sử dụng cột Final_NLP_Rating hiện có.")
        
    # 4. Chuẩn hóa Cột Ngân sách (Giả lập)
    print("Bước 3: Tạo cấp độ Ngân sách (1=Rẻ, 2=TB, 3=Cao)...")
    if 'Price_Level_OSM' not in df.columns:
         # Tạo cấp độ giá ngẫu nhiên
         df['Price_Level_OSM'] = [random.choice([1, 2, 3]) for _ in range(len(df))]
    else:
        print("Sử dụng cột Price_Level_OSM hiện có.")

    # 5. Lưu File Cuối cùng
    # CHỌN CHÍNH XÁC CÁC CỘT MÀ recommender.py CẦN
    REQUIRED_COLUMNS = ['Name', 'Cuisine', 'Latitude', 'Longitude', 'Final_NLP_Rating', 'Price_Level_OSM']
    
    # Lấy các cột bắt buộc, nếu thiếu thì tạo cột rỗng (sẽ gây lỗi nếu không sửa)
    df_output = df.reindex(columns=REQUIRED_COLUMNS).copy()
    
    # Loại bỏ các hàng không có tọa độ (quan trọng)
    df_output.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    
    # Lưu file
    df_output.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    print(f"\n--- TỔNG KẾT ---")
    print(f"Đã tạo file xử lý thành công: {OUTPUT_FILE}")
    print(f"Số nhà hàng sau khi xử lý: {len(df_output)}")

if __name__ == '__main__':
    process_data_pipeline()