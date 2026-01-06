# --- [폰트 로드 함수 업데이트 버전] ---
@st.cache_resource
def load_fonts():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf"
    try:
        response = requests.get(font_url, timeout=10)
        return BytesIO(response.content)
    except Exception as e:
        st.warning(f"폰트 로드 실패: {e}. 기본 폰트를 사용합니다.")
        return None

# --- [이미지 합성 엔진 내 폰트 적용 부분 수정] ---
def create_shorts_image(q_text, names, image_sources, use_sketch_filter):
    # (중략)
    font_bytes = load_fonts()
    try:
        if font_bytes:
            font_title = ImageFont.truetype(font_bytes, 100)
            font_name = ImageFont.truetype(font_bytes, 70)
        else:
            font_title = ImageFont.load_default()
            font_name = ImageFont.load_default()
    except:
        font_title = ImageFont.load_default()
        font_name = ImageFont.load_default()
    # (이하 동일)