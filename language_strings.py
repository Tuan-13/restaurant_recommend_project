# language_strings.py

from google_trans_new import google_translator 
import time
import json 
import os 

# --- THIẾT LẬP CƠ BẢN ---
DEFAULT_LANG = 'VI' 
TARGET_LANGS = {
    'EN': 'en',      
    'JP': 'ja',      
    'KO': 'ko',      
    'ZH': 'zh-cn',   
}

# ID PHIÊN BẢN CHUỖI: THAY ĐỔI KHI CÓ THÊM CHUỖI MỚI VÀ CẦN DỊCH LẠI
STRING_VERSION = "v1.2" 
TRANSLATION_CACHE_FILE = f'translated_strings_cache_{STRING_VERSION}.json'

# --- KHỐI TIẾNG VIỆT (NGÔN NGỮ GỐC) ---
VIETNAMESE_STRINGS = {
    'title': "Gợi ý Nhà hàng Du lịch AI",
    'lang_select': "Chọn Ngôn Ngữ:",
    'location_prompt': "Vị trí hiện tại của bạn:",
    'budget_prompt': "Ngân sách tối đa:",
    'cuisine_prompt': "Khẩu vị/ Loại ẩm thực:",
    'search_button': "Tìm 3 Lựa chọn Tốt Nhất",
    'result_header': "3 Lựa Chọn Hàng Đầu cho Bạn:",
    'cuisine_options': ["Tất cả", "Ẩm thực Việt", "Ẩm thực Á", "Ẩm thực Âu", "Đồ chay"],
    'budget_low': "Giá rẻ",
    'budget_medium': "Giá trung bình",
    'budget_high': "Giá cao",
    'location_format_error': "Vui lòng nhập tọa độ (Lat, Lon) hợp lệ, cách nhau bằng dấu phẩy.",
    'no_location_error': "Vui lòng nhập vị trí hiện tại của bạn.",
    'no_results': "Không tìm thấy nhà hàng nào phù hợp với yêu cầu của bạn trong bán kính 3.5km.",
    'result_table_name': "Tên Nhà Hàng",
    'result_table_cuisine': "Loại Ẩm Thực",
    'result_table_rating': "Điểm Đánh Giá",
    'result_table_distance': "Khoảng Cách (km)"
}

# --- HÀM TẠO TỪ ĐIỂN DỊCH HOÀN CHỈNH ---
def create_full_strings_dict():
    """Tạo từ điển STRINGS hoàn chỉnh bằng cách dịch hoặc đọc từ cache."""
    
    # 1. KIỂM TRA VÀ ĐỌC CACHE
    if os.path.exists(TRANSLATION_CACHE_FILE):
        try:
            with open(TRANSLATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                cached_strings = json.load(f)
                # Đảm bảo cache vẫn chứa ngôn ngữ mặc định
                if DEFAULT_LANG in cached_strings:
                    print(f"--- Đọc chuỗi đã dịch từ cache: {TRANSLATION_CACHE_FILE} ---")
                    return cached_strings
        except:
            print("--- LỖI đọc file cache, tiến hành dịch lại ---")
    
    # Bắt đầu với Tiếng Việt
    full_strings = {DEFAULT_LANG: VIETNAMESE_STRINGS}
    
    try:
        # Khởi tạo đối tượng dịch
        translator = google_translator()
    except Exception as e:
        print(f"LỖI: Không thể khởi tạo Translator. Ứng dụng sẽ chỉ dùng Tiếng Việt. Chi tiết: {e}")
        return full_strings

    print("\n--- Bắt đầu dịch tự động các chuỗi giao diện (sử dụng google-trans-new) ---")
    
    for lang_code, google_code in TARGET_LANGS.items():
        print(f"Đang dịch sang: {lang_code} ({google_code})...")
        translated_dict = {}
        
        # Dịch từng chuỗi
        for key, vn_string in VIETNAMESE_STRINGS.items():
            
            if not vn_string: 
                translated_dict[key] = vn_string
                continue
            
            # Xử lý dịch danh sách (cần dịch từng mục)
            if isinstance(vn_string, list):
                translated_list = []
                for item in vn_string:
                    try:
                        # Dòng này đã đúng cho google_trans_new
                        translated_item = translator.translate(item, lang_src='vi', lang_tgt=google_code)
                        # Lưu ý: google_trans_new đôi khi trả về là chuỗi, đôi khi là list [chuỗi]
                        if isinstance(translated_item, list):
                            translated_item = translated_item[0]
                            
                        translated_list.append(translated_item)
                    except Exception as e:
                        print(f"  --> Cảnh báo: Lỗi dịch '{item}' sang {lang_code}. Dùng bản gốc.")
                        translated_list.append(item) 
                translated_dict[key] = translated_list
            
            # Dịch các chuỗi đơn
            else:
                try:
                    # Dòng này đã đúng cho google_trans_new
                    translated_text = translator.translate(vn_string, lang_src='vi', lang_tgt=google_code)
                    if isinstance(translated_text, list):
                        translated_text = translated_text[0]
                        
                    translated_dict[key] = translated_text
                except Exception as e:
                    print(f"  --> Cảnh báo: Lỗi dịch '{key}' sang {lang_code}. Dùng bản gốc.")
                    translated_dict[key] = vn_string
            
            # Giảm nguy cơ bị chặn
            time.sleep(0.05) 
        
        full_strings[lang_code] = translated_dict
    
    # 2. LƯU KẾT QUẢ DỊCH VÀO FILE JSON
    try:
        with open(TRANSLATION_CACHE_FILE, 'w', encoding='utf-8') as f:
            # Dùng ensure_ascii=False để lưu ký tự Unicode (tiếng Nhật, Hàn,...)
            json.dump(full_strings, f, ensure_ascii=False, indent=4)
        print(f"--- Đã lưu kết quả dịch vào cache: {TRANSLATION_CACHE_FILE} ---")
    except Exception as e:
        print(f"--- CẢNH BÁO: Không thể lưu file cache. Lỗi: {e} ---")
        
    print("--- Dịch hoàn tất. Bắt đầu ứng dụng Streamlit ---")
    return full_strings

STRINGS = create_full_strings_dict()