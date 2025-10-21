# nlp_processor.py

import pandas as pd
import random
from transformers import pipeline

# Load data đã thu thập từ OSM
def load_data(filename='restaurants_osm_data.csv'):
    return pd.read_csv(filename)

def simulate_sentiment_analysis(df):
    """
    Mô phỏng việc tạo ra Review Text (1) và Phân tích Cảm xúc (2).
    """
    
    print("-> Bắt đầu mô phỏng Phân tích Cảm xúc...")
    
    # Danh sách các bình luận mẫu cho mục đích mô phỏng
    positive_reviews = ["Món ăn tuyệt vời, phục vụ nhanh chóng.", "Không gian ấm cúng, trải nghiệm ẩm thực tuyệt hảo.", "Giá cả hợp lý, chắc chắn sẽ quay lại!"]
    negative_reviews = ["Chờ đợi quá lâu, món ăn không như quảng cáo.", "Thái độ nhân viên không tốt, không hài lòng.", "Món ăn quá tệ, không đáng tiền chút nào."]
    
    def generate_simulated_data(row):
        # Tạo Review Text mô phỏng
        if row['Name'] != 'N/A':
            # 50% cơ hội là bình luận tích cực
            if random.random() > 0.5:
                row['Review_Text'] = random.choice(positive_reviews)
                row['Review_Sentiment_Score'] = round(random.uniform(0.6, 1.0), 2) # Điểm cảm xúc cao
            else:
                row['Review_Text'] = random.choice(negative_reviews)
                row['Review_Sentiment_Score'] = round(random.uniform(-1.0, -0.6), 2) # Điểm cảm xúc thấp
        return row

    # Áp dụng hàm mô phỏng
    df = df.apply(generate_simulated_data, axis=1)
    
    print("-> Hoàn thành mô phỏng. Đã gán Review Text và Score.")
    return df

# Thay thế: Hàm Dịch máy (Machine Translation)
# Vì đây là dữ liệu mô phỏng, ta sẽ bỏ qua bước dịch máy phức tạp. 
# Trong thực tế, bạn sẽ dùng HuggingFace/MarianMT để dịch cột Review_Text trước khi phân tích cảm xúc.

def run_nlp_processing():
    df = load_data()
    df_processed = simulate_sentiment_analysis(df)
    
    # Tạm thời sử dụng điểm cảm xúc mô phỏng làm Rating (thay cho Rating API)
    # Lấy giá trị tuyệt đối để Rating luôn dương, sau đó chuẩn hóa
    df_processed['Final_NLP_Rating'] = ((df_processed['Review_Sentiment_Score'] + 1) / 2) * 5 
    df_processed.to_csv('restaurants_processed_data.csv', index=False, encoding='utf-8')
    print("Dữ liệu đã được lưu vào file: restaurants_processed_data.csv")
    return df_processed

if __name__ == "__main__":
    run_nlp_processing()