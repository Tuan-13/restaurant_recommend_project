# language_strings.py

from google_trans_new import google_translator 
import time
import json 
import os 

# --- THIẾT LẬP CƠ BẢN ---
DEFAULT_LANG = 'VI' 
TARGET_LANGS = {
    'EN': 'en', 'JP': 'ja', 'KO': 'ko', 'ZH': 'zh-cn',   
}

# ID PHIÊN BẢN CHUỖI: Đã thay đổi thành v1.5 để buộc dịch lại
STRING_VERSION = "v1.5" 
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
    'budget_low': "Giá rẻ", 'budget_medium': "Giá trung bình", 'budget_high': "Giá cao",
    'location_format_error': "Vui lòng nhập tọa độ (Lat, Lon) hợp lệ, cách nhau bằng dấu phẩy.",
    'no_location_error': "Vui lòng nhập vị trí hiện tại của bạn.",
    'no_results': "Không tìm thấy nhà hàng nào phù hợp với yêu cầu của bạn trong bán kính 3.5km.",
    'result_table_name': "Tên Nhà Hàng",
    'result_table_cuisine': "Loại Ẩm Thực",
    'result_table_rating': "Điểm Đánh Giá",
    'result_table_distance': "Khoảng Cách (km)"
}

# --- HÀM TẠO TỪ ĐIỂN DỊCH HOÀN CHỈNH (CÓ CACHE) ---
def create_full_strings_dict():
    """Tạo từ điển STRINGS hoàn chỉnh bằng cách dịch hoặc đọc từ cache."""
    
    # 1. KIỂM TRA VÀ ĐỌC CACHE
    if os.path.exists(TRANSLATION_CACHE_FILE):
        try:
            with open(TRANSLATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                cached_strings = json.load(f)
                if DEFAULT_LANG in cached_strings:
                    print(f"--- Đọc chuỗi đã dịch từ cache: {TRANSLATION_CACHE_FILE} ---")
                    return cached_strings
        except:
            print("--- LỖI đọc file cache, tiến hành dịch lại ---")
    
    full_strings = {DEFAULT_LANG: VIETNAMESE_STRINGS}
    
    try:
        translator = google_translator()
    except Exception as e:
        print(f"LỖI: Không thể khởi tạo Translator. Chỉ dùng Tiếng Việt. Chi tiết: {e}")
        return full_strings

    print("\n--- Bắt đầu dịch tự động các chuỗi giao diện ---")
    
    for lang_code, google_code in TARGET_LANGS.items():
        print(f"Đang dịch sang: {lang_code} ({google_code})...")
        translated_dict = {}
        
        for key, vn_string in VIETNAMESE_STRINGS.items():
            if not vn_string: translated_dict[key] = vn_string; continue
            
            # Xử lý dịch danh sách và chuỗi
            items_to_translate = vn_string if isinstance(vn_string, list) else [vn_string]
            translated_results = []
            
            for item in items_to_translate:
                try:
                    translated_item = translator.translate(item, lang_src='vi', lang_tgt=google_code)
                    if isinstance(translated_item, list): translated_item = translated_item[0]
                    translated_results.append(translated_item)
                except Exception:
                    translated_results.append(item) 
            
            translated_dict[key] = translated_results if isinstance(vn_string, list) else translated_results[0]
            time.sleep(0.05) 
        
        full_strings[lang_code] = translated_dict
    
    # 2. LƯU KẾT QUẢ DỊCH VÀO FILE JSON
    try:
        with open(TRANSLATION_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(full_strings, f, ensure_ascii=False, indent=4)
        print(f"--- Đã lưu kết quả dịch vào cache: {TRANSLATION_CACHE_FILE} ---")
    except Exception as e:
        print(f"--- CẢNH BÁO: Không thể lưu file cache. Lỗi: {e} ---")
        
    print("--- Dịch hoàn tất. Bắt đầu ứng dụng Streamlit ---")
    return full_strings

STRINGS = create_full_strings_dict()