import streamlit as st
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
from duckduckgo_search import DDGS
import urllib.parse
import os

# --- [1. 기본 설정 및 저장소 준비] ---
st.set_page_config(page_title="쇼츠 생성기 (자동저장+네이버)", page_icon="💾", layout="wide")

# 이미지를 저장할 로컬 폴더 이름
IMAGE_SAVE_DIR = "singer_images"

# 폴더가 없으면 자동으로 생성
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

# --- [2. 비밀번호 보안] ---
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

# --- [3. 데이터: 트래픽 TOP 50명] ---
TROT_SINGERS_TOP50 = [
    "임영웅", "이찬원", "박지현", "영탁", "김호중", "정동원", "장민호", "박서진", "안성훈", "손태진",
    "진해성", "최수호", "송가인", "전유진", "양지은", "김다현", "김태연", "홍지윤", "황영웅", "진욱",
    "박성온", "나상도", "에녹", "신성", "민수현", "김용필", "박구윤", "조명섭", "진성", "김희재",
    "요요미", "장윤정", "나훈아", "남진", "강진", "홍진영", "김연자", "주현미", "마이진", "린",
    "배아현", "정서주", "오유진", "박군", "남승민", "강혜연", "윤수현", "설하윤", "조정민", "은가은"
]

QUIZ_TOPICS = [
    "행사비 가장 비쌀 것 같은 가수는?", "실물 보고 기절초풍한 가수는?", "며느리 삼고 싶은 1위는?",
    "관상학적으로 대박 날 얼굴은?", "타고난 귀티가 흐르는 사람은?", "시어머니 프리패스상 1위는?",
    "팬클럽 화력이 산불급인 가수는?", "CF 몸값 1위 찍을 것 같은 스타?", "가장 섹시한 트로트 스타 1위?",
    "가장 청순한 첫사랑 재질 1위?", "지금 이 순간 가장 빛나는 별!", "영원한 우리의 오빠/언니!"
]

# --- [4. 핵심 기능 함수] ---

def save_image_local(singer_name, uploaded_file):
    """업로드된 파일을 로컬 폴더에 저장"""
    try:
        # 파일명을 '가수이름.jpg'로 저장
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{singer_name}.jpg")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except: return False

def load_image_local(singer_name):
    """로컬 폴더에서 이미지 불러오기"""
    # jpg, png, jpeg 등 확장자 확인
    for ext in ['jpg', 'png', 'jpeg']:
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{singer_name}.{ext}")
        if os.path.exists(file_path):
            try:
                return Image.open(file_path).convert("RGB")
            except: pass
    return None

def fetch_image_secure(url):
    """웹 이미지 다운로드"""
    if not url or not url.startswith("http"): return None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return Image.open(BytesIO(response.content)).convert("RGB")
    except: return None

def search_naver_profile_image(singer_name):
    """네이버 프로필 사진 검색"""
    search_query = f"가수 {singer_name} 네이버 인물정보 프로필 사진"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(search_query, max_results=5))
            for res in results:
                if 'pstatic.net' in res['image'] or 'naver.com' in res['image']:
                    return res['image']
            if results: return results[0]['image']
    except: pass
    return None

@st.cache_resource
def load_fonts():
    url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf"
    try:
        response = requests.get(url, timeout=10)
        return BytesIO(response.content)
    except: return None

def create_shorts_image(q_text, names, image_pil_list, design_settings):
    """최종 합성 (필터 없음)"""
    canvas = Image.new('RGB', (1080, 1920), design_settings['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    font_bytes = load_fonts()
    try:
        if font_bytes:
            font_title = ImageFont.truetype(font_bytes, 100)
            font_bytes.seek(0)
            font_name = ImageFont.truetype(font_bytes, 70)
        else: raise Exception
    except:
        font_title = ImageFont.load_default()
        font_name = ImageFont.load_default()

    # 제목
    try:
        bbox = draw.textbbox((0, 0), q_text, font=font_title)
        text_w = bbox[2] - bbox[0]
        draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill=design_settings['title_color'], align="center")
    except:
        draw.text((100, 150), q_text, fill=design_settings['title_color'])

    positions = [(50, 500), (560, 500), (50, 1100), (560, 1100)]
    size = (470, 550)

    for i, (name, img, pos) in enumerate(zip(names, image_pil_list, positions)):
        if img:
            # 원본 리사이즈 (Crop & Resize)
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
        else:
            img = Image.new('RGB', size, (50, 50, 50))
            # 물음표
            draw_temp = ImageDraw.Draw(img)
            try:
                draw_temp.text((200, 200), "?", fill="white", font=font_title)
            except: pass

        canvas.paste(img, pos)
        
        # 이름표
        tag_w, tag_h = 400, 120
        tag_x = pos[0] + (size[0] - tag_w) // 2
        tag_y = pos[1] + size[1] - (tag_h // 2)
        draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=20, fill=design_settings['tag_bg_color'], outline=design_settings['border_color'], width=5)
        
        try:
            bbox_name = draw.textbbox((0, 0), name, font=font_name)
            name_w = bbox_name[2] - bbox_name[0]
            name_h = bbox_name[3] - bbox_name[1]
            draw.text((tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), name, font=font_name, fill=design_settings['name_color'])
        except:
            draw.text((tag_x + 50, tag_y + 30), name, font=font_name, fill=design_settings['name_color'])

    return canvas

# --- [5. 메인 UI] ---
st.title("💾 쇼츠 생성기 (자동저장 + 네이버)")
st.caption("사진을 한 번만 올리면 자동 저장되어 다음부터는 바로 뜹니다.")

with st.sidebar:
    st.header("🎨 디자인 설정")
    bg_color = st.color_picker("배경색", "#000000")
    title_color = st.color_picker("질문 색", "#FFFF00")
    tag_bg_color = st.color_picker("이름표 배경", "#000000")
    border_color = st.color_picker("테두리 색", "#00FF00")
    name_color = st.color_picker("이름 색", "#00FF00")
    design_settings = {'bg_color': bg_color, 'title_color': title_color, 'tag_bg_color': tag_bg_color, 'border_color': border_color, 'name_color': name_color}

tab_s, tab_t = st.tabs(["👤 인물 선택 (Top 50)", "📝 주제 선택"])
with tab_s:
    s_mode = st.radio("방식", ["랜덤", "직접"], horizontal=True)
    sel_singer = st.selectbox("가수 선택", TROT_SINGERS_TOP50) if s_mode == "직접" else None
with tab_t:
    t_mode = st.radio("방식 ", ["랜덤", "직접"], horizontal=True)
    sel_topic = st.selectbox("주제 선택", QUIZ_TOPICS) if t_mode == "직접" else None

if st.button("🚀 퀴즈 생성하기 (저장된 사진 우선 확인)", type="primary", use_container_width=True):
    with st.spinner("💾 저장소 확인 및 네이버 검색 중..."):
        correct = sel_singer if s_mode == "직접" else random.choice(TROT_SINGERS_TOP50)
        wrongs = random.sample([s for s in TROT_SINGERS_TOP50 if s != correct], 3)
        options = wrongs + [correct]
        random.shuffle(options)
        question = (sel_topic if t_mode == "직접" else random.choice(QUIZ_TOPICS)).format(name=correct)
        
        # 1. 로컬에 저장된게 있는지 먼저 확인 -> 없으면 네이버 검색
        search_results = []
        for s in options:
            if load_image_local(s): # 저장된 파일이 있음
                search_results.append("LOCAL_FOUND")
            else: # 없으면 URL 검색
                search_results.append(search_naver_profile_image(s))
        
        st.session_state['auto_data'] = {'q': question, 'names': options, 'results': search_results}

if 'auto_data' in st.session_state:
    data = st.session_state['auto_data']
    col_l, col_r = st.columns([1, 1.2])
    final_pils = []

    with col_l:
        st.subheader("🛠️ 사진 관리")
        new_q = st.text_area("멘트 수정", value=data['q'])
        
        for i in range(4):
            name = data['names'][i]
            res = data['results'][i]
            st.markdown(f"**{i+1}번: {name}**")
            
            # 이미지 결정 로직 (로컬 우선 -> URL 다운로드)
            current_img = None
            local_file = load_image_local(name) # 혹시 그새 저장됐을 수도 있으니 재확인
            
            if local_file:
                st.success("📂 저장된 사진을 불러왔습니다.")
                st.image(local_file, width=150)
                current_img = local_file
            elif res and res != "LOCAL_FOUND":
                st.info("🌐 네이버 검색 결과입니다.")
                st.image(res, width=150)
                current_img = fetch_image_secure(res)
            else:
                st.warning("사진이 없습니다.")
                q_enc = urllib.parse.quote(f"{name} 프로필")
                st.markdown(f"[네이버 검색 바로가기](https://search.naver.com/search.naver?where=image&query={q_enc})")

            # 업로드 (저장 기능)
            uploaded = st.file_uploader(f"'{name}' 사진 변경/저장", key=f"up_{i}")
            if uploaded:
                save_image_local(name, uploaded) # 저장!
                current_img = Image.open(uploaded).convert("RGB")
                st.toast(f"{name} 사진 저장 완료! 다음엔 자동으로 뜹니다.")
            
            final_pils.append(current_img)
            st.divider()

    with col_r:
        st.subheader("📸 최종 결과물")
        if st.button("✨ 다시 그리기"): pass
        result_img = create_shorts_image(new_q, data['names'], final_pils, design_settings)
        st.image(result_img, use_container_width=True)
        
        buf = BytesIO()
        result_img.save(buf, format="JPEG", quality=100)
        st.download_button("💾 다운로드", buf.getvalue(), file_name="shorts_auto_save.jpg", mime="image/jpeg", type="primary", use_container_width=True)