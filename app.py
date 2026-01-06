import streamlit as st
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import urllib.parse
from duckduckgo_search import DDGS
import cv2
import numpy as np

# --- [기본 설정] ---
st.set_page_config(page_title="쇼츠 자동 생성기 (저작권 보호 Ver)", page_icon="🛡️", layout="wide")

# --- [비밀번호 보안] ---
def check_password():
    if "password_correct" not in st.session_state: st.session_state.password_correct = False
    if st.session_state.password_correct: return True
    st.text_input("비밀번호를 입력하세요", type="password", key="password_input", on_change=password_entered)
    return False
def password_entered():
    if st.session_state["password_input"] == st.secrets["APP_PASSWORD"]:
        st.session_state.password_correct = True
        del st.session_state["password_input"]
    else: st.error("비밀번호가 틀렸습니다.")
if not check_password(): st.stop()

# --- [데이터: 가수 리스트] ---
TROT_SINGERS = ["임영웅","영탁","이찬원","김호중","정동원","장민호","김희재","나훈아","남진","송가인","장윤정","홍진영","박군","박서진","진성","설운도","태진아","송대관","김연자","주현미","양지은","전유진","안성훈","박지현","손태진","에녹","신성","민수현","김다현","김태연","요요미","마이진","린","박구윤","신유","금잔디","조항조","강진","김수희","하춘화","현숙","문희옥","김혜연","진해성","홍지윤","황영웅","공훈","김중연","박민수","나상도","최수호","진욱","박성온","정서주","배아현","오유진","미스김","나영","김소연","정슬","박주희","김수찬","나태주","강혜연","윤수현","조정민","설하윤","류지광","김경민","남승민","황윤성","강태관","김나희","정미애","홍자","정다경","은가은","별사랑","김의영","황민호","황민우","이대원","신인선","노지훈","양지원","한강","재하","신승태","최우진","성리","추혁진","박상철","서주경","한혜진","유지나","김용필","조명섭"]
QUIZ_TEMPLATES = ["2025년 트로트 흐름을\n이끌었던 가수는?", "다음 중 '{name}' 님은\n몇 번일까요?", "이 멋진 무대의 주인공,\n'{name}'을 찾아보세요!"]

# --- [자동 검색 함수 (위키백과 우선)] ---
def search_image_auto(query):
    """저작권 안전지대인 위키미디어/뉴스 위주로 검색"""
    try:
        with DDGS() as ddgs:
            # 1순위: 위키미디어 (가장 안전)
            keywords = [f"{query} wiki image", f"{query} singer performance"]
            for key in keywords:
                results = list(ddgs.images(key, max_results=1))
                if results:
                    return results[0]['image']
    except Exception as e:
        print(f"검색 실패: {e}")
    return None

# --- [핵심: 스케치 효과 변환 함수] ---
def convert_to_sketch(pil_image):
    """사진을 연필 스케치 그림처럼 변환 (저작권 회피용)"""
    # PIL 이미지를 OpenCV 포맷으로 변환
    img_np = np.array(pil_image)
    
    # 흑백 변환
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # 색상 반전
    inverted = 255 - gray
    
    # 흐림 효과 (Blur)
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    
    # 반전된 흐림 이미지를 다시 반전
    inverted_blurred = 255 - blurred
    
    # 스케치 효과 (닷지)
    sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
    
    # 다시 RGB로 변환하여 PIL 이미지로 반환
    return Image.fromarray(cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB))

# --- [폰트 로드] ---
@st.cache_resource
def load_fonts():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf"
    try:
        response = requests.get(font_url, timeout=5)
        return BytesIO(response.content)
    except:
        return None

# --- [이미지 합성 엔진] ---
def create_shorts_image(q_text, names, image_sources, use_sketch_filter):
    canvas = Image.new('RGB', (1080, 1920), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    font_bytes = load_fonts()
    if font_bytes:
        font_title = ImageFont.truetype(font_bytes, 100)
        font_name = ImageFont.truetype(font_bytes, 70)
    else:
        font_title = ImageFont.load_default()
        font_name = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), q_text, font=font_title)
    text_w = bbox[2] - bbox[0]
    draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill="#FFFF00", align="center")

    positions = [(50, 500), (560, 500), (50, 1100), (560, 1100)]
    size = (470, 550)

    for i, (name, source, pos) in enumerate(zip(names, image_sources, positions)):
        img = None
        try:
            if isinstance(source, BytesIO):
                img = Image.open(source).convert("RGB")
            elif isinstance(source, str) and source.startswith("http"):
                response = requests.get(source, timeout=3)
                img = Image.open(BytesIO(response.content)).convert("RGB")
            
            if img:
                # === [여기서 필터 적용!] ===
                if use_sketch_filter:
                    img = convert_to_sketch(img)
                # =========================

                img_ratio = img.width / img.height
                target_ratio = size[0] / size[1]
                if img_ratio > target_ratio:
                    new_width = int(img.height * target_ratio)
                    offset = (img.width - new_width) // 2
                    img = img.crop((offset, 0, offset + new_width, img.height))
                else:
                    new_height = int(img.width / target_ratio)
                    offset = (img.height - new_height) // 2
                    img = img.crop((0, offset, img.width, offset + new_height))
                img = img.resize(size, Image.LANCZOS)
        except:
            img = Image.new('RGB', size, (50, 50, 50))

        if img is None: img = Image.new('RGB', size, (50, 50, 50))
        canvas.paste(img, pos)

        # 이름표
        tag_w, tag_h = 300, 120
        tag_x = pos[0] + (size[0] - tag_w) // 2
        tag_y = pos[1] + size[1] - (tag_h // 2)
        draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=20, fill="black", outline="#00FF00", width=3)
        bbox_name = draw.textbbox((0, 0), name, font=font_name)
        name_w = bbox_name[2] - bbox_name[0]
        name_h = bbox_name[3] - bbox_name[1]
        draw.text((tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), name, font=font_name, fill="#00FF00")

    return canvas

# --- [메인 UI] ---
st.title("🛡️ 쇼츠 자동 생성기 (저작권 회피 모드)")
st.markdown("이미지를 **'스케치 그림'**처럼 변환하여 저작권/초상권 위험을 줄입니다.")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 안전 설정")
    use_sketch = st.checkbox("🎨 스케치 필터 적용 (추천)", value=True, help="사진을 그림처럼 바꿔서 저작권 봇을 피합니다.")

if st.button("🚀 퀴즈 & 이미지 자동 생성", type="primary", use_container_width=True):
    with st.spinner("🤖 저작권 안전지대에서 사진을 찾는 중..."):
        correct_answer = random.choice(TROT_SINGERS)
        wrong_answers = random.sample([s for s in TROT_SINGERS if s != correct_answer], 3)
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        question = random.choice(QUIZ_TEMPLATES).format(name=correct_answer)
        
        auto_urls = []
        for singer in options:
            url = search_image_auto(singer)
            auto_urls.append(url)
        
        st.session_state['auto_data'] = {
            'q': question,
            'names': options,
            'urls': auto_urls
        }

if 'auto_data' in st.session_state:
    data = st.session_state['auto_data']
    
    col_l, col_r = st.columns([1, 1.2])
    
    with col_l:
        st.subheader("🛠️ 사진 확인")
        new_q = st.text_area("질문 멘트", value=data['q'], height=80)
        final_sources = []
        
        for i in range(4):
            st.markdown(f"**{i+1}번: {data['names'][i]}**")
            if data['urls'][i]:
                st.image(data['urls'][i], width=150)
                final_sources.append(data['urls'][i])
            else:
                uploaded = st.file_uploader(f"{data['names'][i]} 직접 업로드", key=f"up_{i}")
                if uploaded: final_sources.append(uploaded)
                else: final_sources.append(None)
            st.divider()

    with col_r:
        st.subheader("📸 최종 결과물")
        if len(final_sources) == 4:
            # 스케치 옵션 적용하여 생성
            final_img = create_shorts_image(new_q, data['names'], final_sources, use_sketch)
            st.image(final_img, caption="완성본 (필터 적용됨)", use_container_width=True)
            
            buf = BytesIO()
            final_img.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            st.download_button("💾 이미지 다운로드", data=byte_im, file_name="shorts_safe.jpg", mime="image/jpeg", type="primary", use_container_width=True)