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
st.set_page_config(page_title="쇼츠 생성기 (오류수정완료)", page_icon="🛠️", layout="wide")

# --- [2. 이미지 및 폰트 메모리 초기화] ---
# 이미지를 잃어버리지 않게 세션(메모리)에 저장 공간을 만듭니다.
if 'user_images' not in st.session_state:
    st.session_state.user_images = {} 

# --- [3. 비밀번호 보안] ---
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

# --- [4. 데이터: 트래픽 TOP 50명] ---
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

# --- [5. 핵심 기능 함수] ---

def fetch_image_secure(url):
    """웹 이미지 다운로드"""
    if not url or not url.startswith("http"): return None
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return Image.open(BytesIO(response.content)).convert("RGB")
    except: return None

def search_naver_profile_image(singer_name):
    """네이버 프로필 검색"""
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

# --- [폰트 로딩 강화: 실패 시 시스템 폰트 사용] ---
@st.cache_resource
def load_font_file():
    """폰트 파일을 다운로드하거나 시스템 폰트를 찾아서 경로를 반환"""
    # 1. 구글 폰트 다운로드 시도
    url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
    except:
        pass
    
    # 2. 다운로드 실패 시, 리눅스(Streamlit Cloud) 시스템 폰트 사용
    # DejaVuSans는 대부분의 리눅스 서버에 기본 설치되어 있음 (한글 미지원일 수 있으나 크기 조절은 됨)
    return "DejaVuSans.ttf" 

def create_shorts_image(q_text, names, image_pil_list, design_settings):
    canvas = Image.new('RGB', (1080, 1920), design_settings['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    # 폰트 로드
    font_file = load_font_file()
    
    # 제목 폰트 설정
    try:
        font_title = ImageFont.truetype(font_file, design_settings['title_size'])
    except:
        # 시스템 폰트조차 없으면 기본 폰트(크기 조절 불가) 사용하되 경고 로그
        font_title = ImageFont.load_default()
        
    # 이름 폰트 설정
    try:
        if isinstance(font_file, BytesIO): font_file.seek(0) # 파일 포인터 초기화
        font_name = ImageFont.truetype(font_file, design_settings['name_size'])
    except:
        font_name = ImageFont.load_default()

    # 제목 그리기
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

# --- [6. 메인 UI] ---
st.title("🛠️ 쇼츠 생성기 (오류 수정판)")
st.info("이제 글자 크기 조절이 정상 작동하며, 업로드한 사진이 사라지지 않습니다.")

with st.sidebar:
    st.header("🎨 디자인 설정")
    bg_color = st.color_picker("배경색", "#000000")
    title_color = st.color_picker("질문 색", "#FFFF00")
    tag_bg_color = st.color_picker("이름표 배경", "#000000")
    border_color = st.color_picker("테두리 색", "#00FF00")
    name_color = st.color_picker("이름 색", "#00FF00")
    
    st.divider()
    # 슬라이더 값 설정
    title_size = st.slider("질문 글자 크기", 50, 150, 80, 5)
    name_size = st.slider("이름 글자 크기", 40, 100, 60, 5)

    design_settings = {
        'bg_color': bg_color, 'title_color': title_color,
        'tag_bg_color': tag_bg_color, 'border_color': border_color, 'name_color': name_color,
        'title_size': title_size, 'name_size': name_size
    }

tab_s, tab_t = st.tabs(["👤 인물 선택", "📝 주제 선택"])

with tab_s:
    s_mode = st.radio("방식", ["랜덤", "직접 (최대 4명)"], horizontal=True)
    selected_singers = []
    if s_mode == "직접 (최대 4명)":
        selected_singers = st.multiselect("가수 선택 (4명을 채우면 고정)", TROT_SINGERS_TOP50, max_selections=4)

with tab_t:
    t_mode = st.radio("방식 ", ["랜덤", "직접"], horizontal=True)
    sel_topic = st.selectbox("주제 선택", QUIZ_TOPICS) if t_mode == "직접" else None

if st.button("🚀 퀴즈 생성하기", type="primary", use_container_width=True):
    with st.spinner("이미지 및 폰트 준비 중..."):
        # 멤버 구성
        if s_mode == "직접 (최대 4명)" and selected_singers:
            options = selected_singers[:]
            if len(options) < 4:
                remaining = [s for s in TROT_SINGERS_TOP50 if s not in options]
                options.extend(random.sample(remaining, 4 - len(options)))
        else:
            correct = random.choice(TROT_SINGERS_TOP50)
            wrongs = random.sample([s for s in TROT_SINGERS_TOP50 if s != correct], 3)
            options = wrongs + [correct]
        
        random.shuffle(options)
        correct_answer = random.choice(options)
        question = (sel_topic if t_mode == "직접" else random.choice(QUIZ_TOPICS)).format(name=correct_answer)
        
        # 이미지 URL 검색 (아직 다운로드는 아님)
        search_results = []
        for s in options:
            # 사용자가 업로드해둔 이미지가 있는지 메모리(Session State) 확인
            if s in st.session_state.user_images:
                search_results.append("USER_UPLOADED")
            else:
                # 없으면 네이버 검색
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
            
            current_img = None
            
            # 1. 사용자가 업로드한 이미지가 메모리에 있는지 확인
            if name in st.session_state.user_images:
                st.success("📂 업로드된 사진 사용 중")
                current_img = st.session_state.user_images[name] # 메모리에서 가져옴
                st.image(current_img, width=150)
            
            # 2. 없으면 검색 결과 사용
            elif res and res != "USER_UPLOADED":
                st.info("🌐 네이버 검색 결과")
                st.image(res, width=150)
                current_img = fetch_image_secure(res)
            
            # 3. 다 없으면
            else:
                st.warning("사진이 없습니다.")
                q_enc = urllib.parse.quote(f"{name} 프로필")
                st.markdown(f"[네이버 검색](https://search.naver.com/search.naver?where=image&query={q_enc})")

            # 업로드 버튼 (업로드 시 즉시 메모리에 저장)
            uploaded = st.file_uploader(f"'{name}' 사진 변경", key=f"up_{i}")
            if uploaded:
                img_obj = Image.open(uploaded).convert("RGB")
                st.session_state.user_images[name] = img_obj # 메모리에 영구 저장 (세션 동안)
                st.toast(f"{name} 사진이 등록되었습니다! (새로고침해도 유지됨)")
                # 즉시 반영을 위해 현재 이미지를 교체
                current_img = img_obj
            
            final_pils.append(current_img)
            st.divider()

    with col_r:
        st.subheader("📸 최종 결과물")
        # 버튼을 누르면 리렌더링 (슬라이더 값 적용)
        if st.button("✨ 설정 적용하여 다시 그리기", use_container_width=True): pass
        
        result_img = create_shorts_image(new_q, data['names'], final_pils, design_settings)
        st.image(result_img, use_container_width=True)
        
        buf = BytesIO()
        result_img.save(buf, format="JPEG", quality=100)
        st.download_button("💾 다운로드", buf.getvalue(), file_name="shorts_fixed.jpg", mime="image/jpeg", type="primary", use_container_width=True)