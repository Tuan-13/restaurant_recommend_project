# language_strings.py

from google_trans_new import Translator
import time # Thêm thư viện time để chờ giữa các lần dịch (giảm nguy cơ bị chặn)

# --- THIẾT LẬP CƠ BẢN ---
# Ngôn ngữ GỐC (Fallback Language) - PHẢI CHỨA TẤT CẢ CÁC KHÓA CHUỖI
DEFAULT_LANG = 'VI' 

# Danh sách ngôn ngữ CẦN DỊCH (Mã Streamlit : Mã Google Translate)
TARGET_LANGS = {
    'EN': 'en',      # English
    'JP': 'ja',      # Japanese
    'KO': 'ko',      # Korean
    'ZH': 'zh-cn',   # Chinese (Giản thể)
}

# --- KHỐI TIẾNG VIỆT (NGÔN NGỮ GỐC) ---
# KHỐI NÀY PHẢI ĐẦY ĐỦ VÀ CHÍNH XÁC. Đây là chuỗi mà bạn sẽ duy trì.
VIETNAMESE_STRINGS = {
    'title': "Gợi ý Nhà hàng Du lịch AI",
    'lang_select': "Chọn Ngôn Ngữ:",
    'location_prompt': "Vị trí hiện tại của bạn:",
    'budget_prompt': "Ngân sách tối đa:",
    'cuisine_prompt': "Khẩu vị/ Loại ẩm thực:",
    'search_button': "Tìm 3 Lựa chọn Tốt Nhất",
    'result_header': "3 Lựa Chọn Hàng Đầu cho Bạn:",
    
    # Danh sách (Cần xử lý đặc biệt)
    'cuisine_options': ["Tất cả", "Ẩm thực Việt", "Ẩm thực Á", "Ẩm thực Âu", "Đồ chay"],
    
    # Các chuỗi ngân sách và lỗi
    'budget_low': "Giá rẻ",
    'budget_medium': "Giá trung bình",
    'budget_high': "Giá cao",
    'location_format_error': "Vui lòng nhập tọa độ (Lat, Lon) hợp lệ, cách nhau bằng dấu phẩy.",
    'no_location_error': "Vui lòng nhập vị trí hiện tại của bạn.",
    'no_results': "Không tìm thấy nhà hàng nào phù hợp với yêu cầu của bạn trong bán kính 3.5km.",
    
    # Tiêu đề bảng kết quả
    'result_table_name': "Tên Nhà Hàng",
    'result_table_cuisine': "Loại Ẩm Thực",
    'result_table_rating': "Điểm Đánh Giá",
    'result_table_distance': "Khoảng Cách (km)"
}

# --- HÀM TẠO TỪ ĐIỂN DỊCH HOÀN CHỈNH ---
def create_full_strings_dict():
    """Tạo từ điển STRINGS hoàn chỉnh bằng cách dịch các chuỗi từ Tiếng Việt."""
    
    # Bắt đầu với Tiếng Việt
    full_strings = {DEFAULT_LANG: VIETNAMESE_STRINGS}
    
    try:
        translator = Translator()
    except Exception as e:
        print(f"LỖI: Không thể khởi tạo Translator. Ứng dụng sẽ chỉ dùng Tiếng Việt. Chi tiết: {e}")
        return full_strings # Trả về chỉ Tiếng Việt nếu lỗi

    print("\n--- Bắt đầu dịch tự động các chuỗi giao diện (sử dụng googletrans) ---")
    
    for lang_code, google_code in TARGET_LANGS.items():
        print(f"Đang dịch sang: {lang_code} ({google_code})...")
        translated_dict = {}
        
        # Dịch từng chuỗi
        for key, vn_string in VIETNAMESE_STRINGS.items():
            
            if not vn_string: # Bỏ qua các chuỗi rỗng
                translated_dict[key] = vn_string
                continue
            
            # Xử lý dịch danh sách (cần dịch từng mục)
            if isinstance(vn_string, list):
                translated_list = []
                for item in vn_string:
                    try:
                        translated_item = translator.translate(item, src='vi', dest=google_code).text
                        translated_list.append(translated_item)
                    except Exception as e:
                        # Nếu dịch lỗi, sử dụng bản gốc (Tiếng Việt)
                        print(f"  --> Cảnh báo: Lỗi dịch '{item}' sang {lang_code}. Dùng bản gốc.")
                        translated_list.append(item) 
                translated_dict[key] = translated_list
            
            # Dịch các chuỗi đơn
            else:
                try:
                    translated_text = translator.translate(vn_string, src='vi', dest=google_code).text
                    translated_dict[key] = translated_text
                except Exception as e:
                    # Nếu dịch lỗi, sử dụng bản gốc (Tiếng Việt)
                    print(f"  --> Cảnh báo: Lỗi dịch '{key}' sang {lang_code}. Dùng bản gốc.")
                    translated_dict[key] = vn_string
            
            # Quan trọng: Dùng sleep để tránh bị Google chặn do gửi quá nhiều request nhanh
            time.sleep(0.05) 
        
        full_strings[lang_code] = translated_dict
    
    print("--- Dịch hoàn tất. Bắt đầu ứng dụng Streamlit ---")
    return full_strings

# Gọi hàm để tạo từ điển chuỗi TỰ ĐỘNG DỊCH
STRINGS = create_full_strings_dict()