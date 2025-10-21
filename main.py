# # main.py

# import streamlit as st
# import pandas as pd
# # Import STRINGS, DEFAULT_LANG, và TARGET_LANGS từ file đã dịch tự động
# from language_strings import STRINGS, DEFAULT_LANG, TARGET_LANGS 
# from recommender import find_best_restaurants

# # --- HÀM CHỌN VÀ THIẾT LẬP NGÔN NGỮ ---
# def get_language_settings():
#     """Hiển thị menu chọn ngôn ngữ và trả về từ điển chuỗi tương ứng."""
    
#     # Tạo danh sách tên ngôn ngữ hiển thị
#     # Kết hợp ngôn ngữ mặc định (VI) và các ngôn ngữ đích (TARGET_LANGS)
#     lang_names = {
#         'VI': 'Tiếng Việt',
#         'EN': 'English',
#         'JP': '日本語 (Nhật)',  
#         'KO': '한국어 (Hàn)',   
#         'ZH': '中文 (Trung)',   
#     }
    
#     # Xác định tất cả các code ngôn ngữ có sẵn trong STRINGS
#     available_lang_codes = list(STRINGS.keys())
    
#     # Dropdown chọn ngôn ngữ (Sử dụng Tiếng Việt cho nhãn)
#     lang_code = st.sidebar.selectbox(
#         STRINGS[DEFAULT_LANG]['lang_select'],
#         options=available_lang_codes, 
#         # Sử dụng format_func để hiển thị tên đầy đủ
#         format_func=lambda x: lang_names.get(x, x) 
#     )
    
#     return STRINGS[lang_code]

# # --- HÀM CHÍNH ---
# def main():
    
#     lang = get_language_settings()
    
#     # SỬ DỤNG TRỰC TIẾP lang['key'] CHO TẤT CẢ CÁC CHUỖI
#     st.title(lang['title'])
#     st.markdown("---")

#     # ... (Tiếp tục sử dụng lang['key'] cho toàn bộ giao diện) ...
#     user_location = st.text_input(
#         lang['location_prompt'], 
#         placeholder=lang['location_format_error'].split(',')[0] # Dùng phần đầu của thông báo lỗi làm placeholder
#     )
    
#     # ... (và tương tự cho tất cả các chuỗi khác) ...

# if __name__ == '__main__':
#     main()
# main.py

import streamlit as st
import pandas as pd
from language_strings import STRINGS, DEFAULT_LANG, TARGET_LANGS 
from recommender import find_best_restaurants

# --- HÀM CHỌN VÀ THIẾT LẬP NGÔN NGỮ ---
# Hàm này giữ nguyên như bạn đã cung cấp
def get_language_settings():
    """Hiển thị menu chọn ngôn ngữ và trả về từ điển chuỗi tương ứng."""
    
    lang_names = {
        'VI': 'Tiếng Việt',
        'EN': 'English',
        'JP': '日本語 (Nhật)',  
        'KO': '한국어 (Hàn)',   
        'ZH': '中文 (Trung)',   
    }
    
    available_lang_codes = list(STRINGS.keys())
    
    lang_code = st.sidebar.selectbox(
        STRINGS[DEFAULT_LANG]['lang_select'],
        options=available_lang_codes, 
        format_func=lambda x: lang_names.get(x, x) 
    )
    
    return STRINGS[lang_code]

# --- HÀM CHÍNH ---
def main():
    
    lang = get_language_settings()
    
    st.title(lang['title'])
    st.markdown("---")

    # --- 1. GIAO DIỆN NHẬP LIỆU ---
    user_location = st.text_input(
        lang['location_prompt'], 
        placeholder="VD: 21.03, 105.85 (Tọa độ Lat,Lon)"
    )

    col1, col2 = st.columns(2)

    with col1:
        # Ngân sách (Price Level)
        budget_options = {
            1: lang['budget_low'], 
            2: lang['budget_medium'], 
            3: lang['budget_high']
        }
        user_budget = st.select_slider(
            lang['budget_prompt'],
            options=[1, 2, 3],
            format_func=lambda x: budget_options[x],
            value=2
        )

    with col2:
        # Khẩu vị/Loại ẩm thực
        # Sử dụng danh sách cuisine_options đã được dịch tự động
        user_cuisine = st.selectbox(
            lang['cuisine_prompt'],
            options=lang['cuisine_options']
        )
    
    st.markdown("---")

    # --- 2. NÚT TÌM KIẾM VÀ LOGIC XỬ LÝ ---
    if st.button(lang['search_button']):
        
        # 2.1. Kiểm tra và xử lý Vị trí
        if not user_location:
            st.error(lang['no_location_error'])
            return
            
        try:
            # Tách chuỗi tọa độ thành Lat và Lon
            lat, lon = map(float, user_location.replace(" ", "").split(','))
        except ValueError:
            st.error(lang['location_format_error'])
            return

        with st.spinner('Đang tìm kiếm và phân tích...'):
            
            # 2.2. GỌI MÔ HÌNH GỢI Ý (từ recommender.py)
            results_df = find_best_restaurants(
                user_cuisine, 
                user_budget, 
                lat, 
                lon
            )
        
        # 2.3. HIỂN THỊ KẾT QUẢ
        st.header(lang['result_header'])
        
        if results_df.empty:
            st.warning(lang['no_results'])
        else:
            # Đổi tên cột cho phù hợp với ngôn ngữ hiển thị
            display_df = results_df.rename(columns={
                'Name': lang['result_table_name'],
                'Cuisine': lang['result_table_cuisine'],
                'Final_NLP_Rating': lang['result_table_rating'],
                'Distance_km': lang['result_table_distance']
            })
            
            # Làm tròn các cột số
            display_df[lang['result_table_rating']] = display_df[lang['result_table_rating']].round(2).astype(str) + ' ⭐'
            display_df[lang['result_table_distance']] = display_df[lang['result_table_distance']].round(2).astype(str) + ' km'
            
            # Hiển thị kết quả dưới dạng bảng
            st.table(display_df)
            
            st.success(f"Đã gợi ý {len(results_df)} nhà hàng phù hợp nhất!")


if __name__ == '__main__':
    # Streamlit sẽ chạy hàm main()
    main()