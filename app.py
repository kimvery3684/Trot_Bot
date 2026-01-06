import streamlit as st
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import cv2
import numpy as np
from duckduckgo_search import DDGS
import urllib.parse
import os

# --- [1. 기본 설정 & 폴더 생성] ---
st.set_page_config(page_title="쇼츠 자동 생성기 (자동저장 Ver)", page_icon="💾", layout="wide")

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

# --- [3. 데이터 설정] ---
TROT_SINGERS = [
    "임영웅","영탁","이찬원","김호중","정동원","장민호","김희재","나훈아","남진","송가인",
    "장윤정","홍진영","박군","박서진","진성","설운도","태진아","송대관","김연자","주현미",
    "양지은","전유진","안성훈","박지현","손태진","에녹","신성","민수현","김다현","김태연",
    "요요미","마이진","린","박구윤","신유","금잔디","조항조","강진","김수희","하춘화",
    "현숙","문희옥","김혜연","진해성","홍지윤","황영웅","공훈","김중연","박민수","나상도",
    "최수호","진욱","박성온","정서주","배아현","오유진","미스김","나영","김소연","정슬",
    "박주희","김수찬","나태주","강혜연","윤수현","조정민","설하윤","류지광","김경민","남승민",
    "황윤성","강태관","김나희","정미애","홍자","정다경","은가은","별사랑","김의영","황민호",
    "황민우","이대원","신인선","노지훈","양지원","한강","재하","신승태","최우진","성리",
    "추혁진","박상철","서주경","한혜진","유지나","김용필","조명섭","지원이","윙크","소유미",
    "강예슬","김소유","두리","박성연","장하온","한담희","현진우","최진희","심수봉","이용",
    "조용필","최백호","윤항기","김국환","편승엽","오승근","이자연","김용임","서지오","김혜림"
]

QUIZ_TOPICS = [
    "행사비 가장 비쌀 것 같은 가수는?", "재산 1000억 넘을 것 같은 관상은?", "실물 보고 기절초풍한 가수는?", 
    "성형외과 의사가 뽑은 완벽한 얼굴?", "시어머니 프리패스상 1위는?", "며느리 삼고 싶은 1위는?",
    "관상학적으로 대박 날 얼굴은?", "노년이 가장 편안할 것 같은 관상은?", "빚보증 서줘도 될 의리파는?",
    "화나면 제일 무서울 것 같은 사람은?", "첫사랑 기억 조작하는 얼굴 1위?", "학창시절 일진이었을 것 같은 포스?",
    "공부 1등 했을 것 같은 모범생 관상은?", "타고난 귀티가 흐르는 사람은?", "가장 짠돌이/짠순이일 것 같은?",
    "술 가장 잘 마실 것 같은 주당은?", "눈물 많아 보호본능 자극하는 1위?", "사기꾼도 도망갈 기센 관상은?",
    "요리 실력 장금이 뺨칠 것 같은?", "건물주 포스 철철 넘치는 사람은?", "부모님께 집 사드렸을 효자는?",
    "팬들에게 역조공 제일 많이 할 듯한?", "실제로 보면 얼굴 제일 작을 듯한?", "다리 길이 2미터 모델 비율은?",
    "한복 핏이 조선시대 왕족급인?", "수트 핏이 재벌 3세 같은 사람은?", "애교가 철철 넘치는 인간 복숭아?",
    "무대 위랑 아래가 완전 다른 반전캐?", "가장 빨리 결혼할 것 같은 스타는?", "평생 혼자 살 것 같은 철벽남/녀?",
    "목소리 보험 가입해야 할 국보급 1위?", "고음 올리다 유리창 깰 것 같은?", "라이브 듣고 소름 돋은 가수 1위?",
    "트로트 안 했으면 개그맨 했을 끼?", "연기자로 데뷔해도 대박 날 얼굴?", "CF 몸값 1위 찍을 것 같은 스타?",
    "걸어 다니는 중소기업! 매출 1위?", "팬클럽 화력이 산불급인 가수는?", "댓글부대 몰고 다니는 이슈메이커?",
    "안티팬도 팬으로 만들 매력 부자?", "밥 가장 잘 사줄 것 같은 형/누나?", "후배 군기 제일 잡을 것 같은?",
    "선배들에게 가장 예쁨 받을 애교쟁이?", "사복 패션 센스 꽝일 것 같은?", "명품이 가장 잘 어울리는 인간 명품?",
    "피부가 백옥 같아 눈부신 1위?", "근육질 몸매가 성난 황소 같은?", "다이어트 자극 짤 생성기 1위?",
    "먹방 찍으면 유튜브 떡상할 스타?", "나이 거꾸로 먹는 동안 종결자?", "환갑 때도 20대 같을 것 같은?",
    "가장 로또 맞은 것 같은 인생 역전?", "무명 시절 가장 길었을 것 같은?", "연습생 기간 없이 바로 떴을 천재?",
    "작곡가들이 곡 주고 싶어 줄 설 1위?", "듀엣 하면 무조건 1위 할 조합?", "해외 진출하면 빌보드 씹어먹을?",
    "북한에서도 인기 많을 것 같은?", "통일 되면 평양 공연 갈 1순위?", "사극 찍으면 시청률 50% 찍을 관상?",
    "예능 나가면 고정 꿰찰 입담꾼?", "유재석도 감당 못할 텐션 부자?", "강호동이랑 씨름해도 이길 장사?",
    "축구 국가대표 해도 될 피지컬?", "아이돌 센터 해도 센터 먹을 비주얼?", "걸그룹/보이그룹 멤버였으면 리더?",
    "팬서비스 하다가 꿀 떨어질 눈빛?", "사인회 줄이 지구 한 바퀴일 듯한?", "콘서트 티켓팅 피 튀길 것 같은?",
    "암표 가격이 제일 비쌀 것 같은?", "고속도로 휴게소 음반 판매왕?", "어르신들 휴대폰 배경화면 점유율 1위?",
    "노래방 애창곡 순위 도배할 가수?", "행사 스케줄 1년치 꽉 찼을 듯한?", "헬기 타고 행사 다닐 것 같은?",
    "군대 가면 포상휴가 싹쓸이할?", "군통령/군장병의 여신 등극할?", "가장 섹시한 트로트 스타 1위?",
    "가장 청순한 첫사랑 재질 1위?", "가장 터프한 상남자 포스 1위?", "가장 러블리한 인간 비타민 1위?",
    "목소리에 한(恨)이 서려 있는?", "듣자마자 눈물 콧물 쏟게 하는?", "사이다 100개 마신 듯 뻥 뚫리는?",
    "막걸리 광고 모델로 딱인 1위?", "소주 광고 모델로 딱인 1위?", "맥주 광고 모델로 딱인 1위?",
    "화장품 광고 모델로 딱인 피부?", "건강보조식품 완판시킬 신뢰감?", "은행 광고 모델로 딱인 신뢰감?",
    "국회의원 출마하면 당선될 관상?", "뉴스 앵커 해도 잘할 딕션?", "동물농장 성우 하면 딱일 목소리?",
    "가장 4차원일 것 같은 엉뚱 매력?", "몰래카메라 당하면 대성통곡할?", "귀신 나오면 기절할 것 같은 겁쟁이?",
    "무인도에 떨어져도 살아남을 생존력?", "팬이랑 결혼할 수도 있을 로맨티스트?"
]

# --- [4. 핵심 기능: 로컬 저장소 및 검색] ---

def save_image_local(singer_name, uploaded_file):
    """업로드된 파일을 로컬 폴더에 저장"""
    try:
        # 파일 확장자 확인 (기본 jpg)
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{singer_name}.jpg")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except:
        return False

def load_image_local(singer_name):
    """로컬 폴더에서 이미지 불러오기"""
    # jpg, png, jpeg 순서로 확인
    for ext in ['jpg', 'png', 'jpeg']:
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{singer_name}.{ext}")
        if os.path.exists(file_path):
            try:
                return Image.open(file_path).convert("RGB")
            except: pass
    return None

def fetch_image_secure(url):
    """봇 차단 우회하여 이미지 다운로드"""
    if not url or not url.startswith("http"): return None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    except Exception: return None

def search_image_naver(query, client_id, client_secret):
    """네이버 API 검색"""
    url = "https://openapi.naver.com/v1/search/image"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    params = {"query": f"{query} 고화질 프로필", "display": 1, "start": 1, "sort": "sim", "filter": "medium"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            items = res.json().get('items', [])
            if items: return items[0]['link']
    except: pass
    return None

def search_image_hybrid(query, naver_keys):
    """1순위: 로컬 저장소 -> 2순위: 네이버 -> 3순위: 덕덕고"""
    
    # 1. 로컬 저장소 확인 (가장 빠름)
    local_img = load_image_local(query)
    if local_img: return "LOCAL_FOUND"

    # 2. 네이버 API
    if naver_keys['id'] and naver_keys['secret']:
        img_url = search_image_naver(query, naver_keys['id'], naver_keys['secret'])
        if img_url: return img_url
    
    # 3. 덕덕고
    search_terms = [f"{query} wiki image", f"{query} singer", f"{query} 트로트"]
    try:
        with DDGS() as ddgs:
            for term in search_terms:
                results = list(ddgs.images(term, max_results=1))
                if results: return results[0]['image']
    except: pass
    return None

def convert_to_sketch(pil_image):
    """스케치 필터"""
    try:
        img_np = np.array(pil_image)
        if len(img_np.shape) == 2: gray = img_np
        else: gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        inverted = 255 - gray
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blurred = 255 - blurred
        sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
        return Image.fromarray(cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB))
    except: return pil_image

@st.cache_resource
def load_fonts():
    """폰트 로드"""
    urls = [
        "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
    ]
    for url in urls:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200: return BytesIO(response.content)
        except: continue
    return None

def create_shorts_image(q_text, names, final_images, design_settings):
    """최종 이미지 합성"""
    canvas = Image.new('RGB', (1080, 1920), design_settings['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    font_bytes = load_fonts()
    font_title = None
    font_name = None

    if font_bytes:
        try:
            font_title = ImageFont.truetype(font_bytes, 100)
            font_bytes.seek(0)
            font_name = ImageFont.truetype(font_bytes, 70)
        except: pass

    if font_title is None:
        sys_fonts = ["malgun.ttf", "NanumGothic.ttf", "arial.ttf", "AppleGothic.ttf"]
        for f in sys_fonts:
            try:
                font_title = ImageFont.truetype(f, 100)
                font_name = ImageFont.truetype(f, 70)
                break
            except: continue

    if font_title is None:
        font_title = ImageFont.load_default()
        font_name = ImageFont.load_default()

    # 질문
    try:
        bbox = draw.textbbox((0, 0), q_text, font=font_title)
        text_w = bbox[2] - bbox[0]
        draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill=design_settings['title_color'], align="center")
    except:
        draw.text((100, 150), q_text, fill=design_settings['title_color'])

    positions = [(50, 500), (560, 500), (50, 1100), (560, 1100)]
    size = (470, 550)

    for i, (name, img, pos) in enumerate(zip(names, final_images, positions)):
        # 이미지 처리 (이미 PIL 객체로 넘어옴)
        if img:
            img = convert_to_sketch(img)
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
            draw_temp = ImageDraw.Draw(img)
            draw_temp.text((200, 200), "?", fill="white", font=font_title)

        canvas.paste(img, pos)
        
        # 이름표
        tag_w, tag_h = 300, 120
        tag_x = pos[0] + (size[0] - tag_w) // 2
        tag_y = pos[1] + size[1] - (tag_h // 2)
        
        draw.rounded_rectangle(
            [tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], 
            radius=20, 
            fill=design_settings['tag_bg_color'], 
            outline=design_settings['border_color'], 
            width=3
        )
        
        try:
            bbox_name = draw.textbbox((0, 0), name, font=font_name)
            name_w = bbox_name[2] - bbox_name[0]
            name_h = bbox_name[3] - bbox_name[1]
            draw.text(
                (tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), 
                name, 
                font=font_name, 
                fill=design_settings['name_color']
            )
        except:
             draw.text((tag_x + 50, tag_y + 30), name, font=font_name, fill=design_settings['name_color'])

    return canvas

# --- [5. 메인 UI] ---
st.title("💾 쇼츠 자동 생성기 (자동저장 Ver)")
st.caption(f"사진을 직접 업로드하면 '{IMAGE_SAVE_DIR}' 폴더에 저장되어, 다음부터는 자동으로 불러옵니다.")

# === [사이드바] ===
with st.sidebar:
    st.header("🎨 디자인 설정")
    bg_color = st.color_picker("배경색", "#000000")
    title_color = st.color_picker("질문 색", "#FFFF00")
    tag_bg_color = st.color_picker("이름표 배경", "#000000")
    border_color = st.color_picker("테두리 색", "#00FF00")
    name_color = st.color_picker("이름 색", "#00FF00")
    design_settings = {'bg_color': bg_color, 'title_color': title_color, 'tag_bg_color': tag_bg_color, 'border_color': border_color, 'name_color': name_color}

    st.divider()
    st.header("네이버 API (선택)")
    n_id = st.text_input("Client ID", key="n_id")
    n_secret = st.text_input("Client Secret", type="password", key="n_secret")
    naver_keys = {'id': n_id, 'secret': n_secret}

# === [메인 탭] ===
tab_singer, tab_topic = st.tabs(["👤 인물", "📝 주제"])
with tab_singer:
    singer_mode = st.radio("인물 선택", ["랜덤", "직접"], horizontal=True, key="s_mode")
    selected_main_singer = st.selectbox("가수 목록", TROT_SINGERS, key="s_select") if singer_mode == "직접" else None
with tab_topic:
    topic_mode = st.radio("주제 선택", ["랜덤", "직접"], horizontal=True, key="t_mode")
    selected_quiz_topic = st.selectbox("주제 목록", QUIZ_TOPICS, key="t_select") if topic_mode == "직접" else None

st.divider()

if st.button("🚀 퀴즈 생성하기", type="primary", use_container_width=True):
    with st.spinner("💾 저장된 사진 확인 중... (없으면 검색)"):
        if singer_mode == "직접": correct_answer = selected_main_singer
        else: correct_answer = random.choice(TROT_SINGERS)
        
        wrong_answers = random.sample([s for s in TROT_SINGERS if s != correct_answer], 3)
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        
        question = selected_quiz_topic.format(name=correct_answer) if topic_mode == "직접" else random.choice(QUIZ_TOPICS).format(name=correct_answer)
        
        # URL 또는 로컬 식별자 수집
        results = []
        for singer in options:
            res = search_image_hybrid(singer, naver_keys)
            results.append(res)
        
        st.session_state['auto_data'] = {
            'q': question,
            'names': options,
            'results': results # URL or "LOCAL_FOUND"
        }

if 'auto_data' in st.session_state:
    data = st.session_state['auto_data']
    col_l, col_r = st.columns([1, 1.2])
    
    # 최종적으로 PIL 이미지들을 담을 리스트
    final_pil_images = []

    with col_l:
        st.subheader("🛠️ 사진 확인")
        new_q = st.text_area("질문 멘트", value=data['q'], height=80)
        
        for i in range(4):
            singer_name = data['names'][i]
            search_res = data['results'][i]
            
            st.markdown(f"**{i+1}번: {singer_name}**")
            
            current_img = None
            
            # 1. 로컬에 저장된 파일이 있는지 확인
            local_file = load_image_local(singer_name)
            
            if local_file:
                st.success("📂 저장된 사진을 불러왔습니다!")
                st.image(local_file, width=150)
                current_img = local_file
            
            # 2. 로컬에 없지만 검색 결과(URL)가 있는 경우
            elif search_res and search_res != "LOCAL_FOUND":
                st.info("🌐 인터넷 검색 결과입니다.")
                st.image(search_res, width=150)
                # URL 이미지를 다운로드해서 current_img로 설정
                current_img = fetch_image_secure(search_res)
            
            # 3. 아무것도 없는 경우 (직접 업로드 필요)
            else:
                st.warning("사진이 없습니다. 직접 올려주세요.")
                # 구글 링크 등 제공
                q_enc = urllib.parse.quote(f"{singer_name} 고화질")
                st.markdown(f"[구글 검색](https://www.google.com/search?q={q_enc}&tbm=isch)")

            # 업로드 버튼 (항상 표시 - 마음에 안 들면 바꾸라고)
            uploaded = st.file_uploader(f"'{singer_name}' 사진 업로드/변경 (자동저장됨)", key=f"up_{i}")
            
            if uploaded:
                # 업로드하면 -> 로컬에 저장하고 -> 그걸 사용
                save_image_local(singer_name, uploaded)
                current_img = Image.open(uploaded).convert("RGB")
                st.toast(f"{singer_name} 사진이 저장되었습니다! 다음엔 자동으로 뜹니다.")
            
            final_pil_images.append(current_img)
            st.divider()

    with col_r:
        st.subheader("📸 최종 결과물")
        if st.button("✨ 다시 그리기", use_container_width=True): pass
        
        final_img = create_shorts_image(new_q, data['names'], final_pil_images, design_settings)
        st.image(final_img, caption="완성본", use_container_width=True)
        
        buf = BytesIO()
        final_img.save(buf, format="JPEG", quality=95)
        st.download_button("💾 다운로드", data=buf.getvalue(), file_name="shorts_auto.jpg", mime="image/jpeg", type="primary", use_container_width=True)