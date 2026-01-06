import streamlit as st
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
from duckduckgo_search import DDGS
import urllib.parse
import os

# --- [1. 기본 설정] ---
st.set_page_config(page_title="쇼츠 생성기 (완전해결판)", page_icon="⚡", layout="wide")

# 이미지를 저장할 메모리 공간 초기화 (새로고침해도 사진 안 날아가게 함)
if 'cached_images' not in st.session_state:
    st.session_state.cached_images = {}

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

# --- [3. 데이터 설정] ---
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

# --- [4. 폰트 로딩 (로컬 파일 우선)] ---
def get_font(size):
    """
    1순위: 같은 폴더에 있는 NanumGothic-ExtraBold.ttf 파일 사용
    2순위: 없으면 웹에서 다운로드 시도
    """
    font_filename = "NanumGothic-ExtraBold.ttf"
    
    # 1. 로컬 파일 확인
    if os.path.exists(font_filename):
        return ImageFont.truetype(font_filename, size)
    
    # 2. 로컬에 없으면 웹 다운로드 (비상용)
    url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf"
    try:
        response = requests.get(url, timeout=5)
        return ImageFont.truetype(BytesIO(response.content), size)
    except:
        # 3. 진짜 다 실패하면 기본 폰트 (깨질 수 있음)
        return ImageFont.load_default()

# --- [5. 이미지 검색 및 처리] ---
def fetch_image_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        return Image.open(BytesIO(response.content)).convert("RGB")
    except: return None

def search_naver_image(query):
    try:
        with DDGS() as ddgs:
            # 네이버 프로필 느낌의 검색어
            keywords = [f"가수 {query} 프로필", f"{query} 화보 고화질", f"{query} 얼굴"]
            for key in keywords:
                results = list(ddgs.images(key, max_results=2))
                if results: return results[0]['image']
    except: pass
    return None

def create_final_image(q_text, names, images, design):
    canvas = Image.new('RGB', (1080, 1920), design['bg'])
    draw = ImageDraw.Draw(canvas)
    
    # 폰트 로드
    font_title = get_font(design['t_size'])
    font_name = get_font(design['n_size'])
    
    # 질문 그리기
    try:
        bbox = draw.textbbox((0, 0), q_text, font=font_title)
        text_w = bbox[2] - bbox[0]
        draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill=design['t_color'], align="center")
    except:
        # 폰트 깨짐 방지용 영문 출력
        draw.text((100, 150), "Font Error", fill="red")

    # 이미지 배치
    positions = [(50, 500), (560, 500), (50, 1100), (560, 1100)]
    size = (470, 550)

    for i, (name, img, pos) in enumerate(zip(names, images, positions)):
        # 이미지 없으면 회색 박스
        if img is None:
            img = Image.new('RGB', size, (50, 50, 50))
        
        # 리사이즈 & 크롭
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
        canvas.paste(img, pos)

        # 이름표
        tag_w, tag_h = 400, 120
        tag_x = pos[0] + (size[0] - tag_w) // 2
        tag_y = pos[1] + size[1] - (tag_h // 2)
        
        draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=20, fill=design['tag_bg'], outline=design['border'], width=5)
        
        # 이름 그리기
        try:
            bbox_name = draw.textbbox((0, 0), name, font=font_name)
            name_w = bbox_name[2] - bbox_name[0]
            name_h = bbox_name[3] - bbox_name[1]
            draw.text((tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), name, font=font_name, fill=design['n_color'])
        except: pass

    return canvas

# --- [6. 메인 UI] ---
st.title("⚡ 쇼츠 생성기 (폰트파일 필수)")
st.warning("주의: 'NanumGothic-ExtraBold.ttf' 파일이 같은 폴더에 없으면 글자가 깨집니다.")

# 사이드바 디자인
with st.sidebar:
    st.header("🎨 디자인")
    bg_color = st.color_picker("배경색", "#000000")
    t_color = st.color_picker("질문 색", "#FFFF00")
    tag_bg = st.color_picker("이름표 배경", "#000000")
    border = st.color_picker("테두리 색", "#00FF00")
    n_color = st.color_picker("이름 색", "#00FF00")
    
    st.divider()
    t_size = st.slider("질문 크기", 50, 150, 90)
    n_size = st.slider("이름 크기", 40, 120, 65)

    design = {
        'bg': bg_color, 't_color': t_color, 'tag_bg': tag_bg, 
        'border': border, 'n_color': n_color, 't_size': t_size, 'n_size': n_size
    }

# 탭 구성
tab1, tab2 = st.tabs(["가수 선택", "주제 선택"])
with tab1:
    mode = st.radio("모드", ["랜덤", "직접 (최대 4명)"], horizontal=True)
    sel_singers = []
    if mode == "직접 (최대 4명)":
        sel_singers = st.multiselect("가수", TROT_SINGERS_TOP50, max_selections=4)

with tab2:
    q_mode = st.radio("질문 모드", ["랜덤", "직접"], horizontal=True)
    sel_topic = st.selectbox("주제", QUIZ_TOPICS) if q_mode == "직접" else None

# 생성 버튼
if st.button("🚀 퀴즈 만들기", type="primary", use_container_width=True):
    # 1. 멤버 구성
    if mode == "직접 (최대 4명)" and sel_singers:
        options = sel_singers[:]
        if len(options) < 4:
            rem = [s for s in TROT_SINGERS_TOP50 if s not in options]
            options.extend(random.sample(rem, 4 - len(options)))
    else:
        correct = random.choice(TROT_SINGERS_TOP50)
        wrongs = random.sample([s for s in TROT_SINGERS_TOP50 if s != correct], 3)
        options = wrongs + [correct]
    
    random.shuffle(options)
    
    # 2. 질문 선정
    winner = random.choice(options)
    question = (sel_topic if q_mode == "직접" else random.choice(QUIZ_TOPICS)).format(name=winner)
    
    # 3. 데이터 세션 저장 (이미지는 아직 URL만)
    st.session_state['quiz_data'] = {
        'q': question,
        'names': options,
        'urls': [search_naver_image(s) for s in options]
    }

# 결과 화면
if 'quiz_data' in st.session_state:
    data = st.session_state['quiz_data']
    col1, col2 = st.columns([1, 1.2])
    
    final_images = []

    with col1:
        st.subheader("🖼️ 이미지 관리")
        new_q = st.text_area("멘트 수정", value=data['q'])
        
        for i in range(4):
            name = data['names'][i]
            url = data['urls'][i]
            
            st.markdown(f"**{i+1}. {name}**")
            
            # 이미지 우선순위: 1.업로드한거(캐시) -> 2.검색된거
            current_img = None
            
            # 캐시에 있는지 확인
            if name in st.session_state.cached_images:
                current_img = st.session_state.cached_images[name]
                st.success("✅ 업로드 사진 사용 중")
            elif url:
                # 검색된 URL 다운로드 (캐시에 없을때만)
                current_img = fetch_image_from_url(url)
            
            # 화면 표시
            if current_img:
                st.image(current_img, width=150)
            else:
                st.warning("사진 없음")
                q_enc = urllib.parse.quote(f"{name} 고화질")
                st.markdown(f"[네이버 검색](https://search.naver.com/search.naver?where=image&query={q_enc})")

            # 업로드 기능 (여기서 업로드하면 즉시 캐시에 저장)
            uploaded = st.file_uploader(f"{name} 사진 변경", key=f"up_{i}")
            if uploaded:
                # 파일 읽어서 세션에 영구 저장
                img_obj = Image.open(uploaded).convert("RGB")
                st.session_state.cached_images[name] = img_obj
                st.toast(f"{name} 사진 저장됨! (사라지지 않음)")
                st.rerun() # 즉시 반영을 위해 새로고침
            
            final_images.append(current_img)
            st.divider()

    with col2:
        st.subheader("✨ 결과물")
        # 버튼 눌러도 업로드 사진 유지됨
        if st.button("🎨 디자인 적용하여 다시 그리기", use_container_width=True): pass
        
        result = create_final_image(new_q, data['names'], final_images, design)
        st.image(result, use_container_width=True)
        
        buf = BytesIO()
        result.save(buf, format="JPEG", quality=100)
        st.download_button("💾 다운로드", buf.getvalue(), "shorts.jpg", "image/jpeg", type="primary", use_container_width=True)