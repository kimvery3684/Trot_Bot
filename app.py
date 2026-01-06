import streamlit as st
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import cv2
import numpy as np
from duckduckgo_search import DDGS
import urllib.parse # 링크 생성을 위한 라이브러리 추가

# --- [1. 기본 설정] ---
st.set_page_config(page_title="쇼츠 자동 생성기 (검색 링크 지원)", page_icon="🛡️", layout="wide")

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
    "2025년 트로트계를 평정한 가수는?", "가장 감성적인 보이스의 주인공은?", "퍼포먼스의 제왕은 누구일까요?", 
    "다음 중 '{name}' 님은 어디에?", "효도 관광 함께 가고 싶은 가수 1위는?", "트로트계의 아이돌, 이 사람은?",
    "천상의 고음을 가진 가수는?", "행사의 여왕/제왕은 누구?", "첫사랑 기억 조작하게 만드는 가수는?",
    "실물이 더 빛나는 가수는 누구?", "팬바보로 소문난 가수는?", "한복이 가장 잘 어울리는 사람은?",
    "트로트 신동에서 거장으로!", "국민 사위/며느리 삼고 싶은 1위는?", "고속도로 아이돌이라 불리는 사람은?",
    "전설의 무대를 남긴 주인공은?", "작곡가들이 사랑하는 목소리는?", "예능감까지 갖춘 만능 엔터테이너는?",
    "비 오는 날 듣고 싶은 목소리는?", "꿀 떨어지는 눈빛의 소유자는?", "지치지 않는 체력의 소유자는?",
    "팬클럽 화력이 가장 뜨거운 가수는?", "광고계를 휩쓴 블루칩은?", "차세대 트로트 황제는?",
    "정통 트로트의 계보를 잇는 자는?", "퓨전 트로트의 선두주자는?", "가장 스타일리시한 트로트 스타는?",
    "안경이 잘 어울리는 지적인 이미지는?", "미소가 아름다운 스마일맨은?", "카리스마 넘치는 무대 장인은?",
    "눈물샘을 자극하는 감동의 목소리는?", "사이다 같은 시원한 가창력은?", "귀공자/공주님 같은 외모는?",
    "반전 매력의 소유자는?", "연기까지 섭렵한 만능캐는?", "순수 청년 이미지의 가수는?",
    "독보적인 음색 깡패는?", "무대 위 댄스 머신은?", "라디오 DJ로도 활약한 사람은?",
    "군통령이라 불리는 가수는?", "오디션 프로그램 우승 후보 0순위였던?", "최단기간 전석 매진 신화의 주인공?",
    "해외에서도 통할 글로벌 스타는?", "슈트핏/드레스핏이 완벽한 사람은?", "애교가 가장 많은 멤버는?",
    "리더십이 뛰어난 맏형/맏언니는?", "팀의 막내 같은 동안 외모는?", "요리까지 잘하는 1등 신랑/신부감은?",
    "축구/운동을 사랑하는 건강 미남/미녀는?", "팬서비스가 가장 혜자로운 스타는?", "성대모사를 잘하는 재간둥이는?",
    "트로트 차트 1위를 가장 오래한 사람은?", "듀엣 무대를 함께 하고픈 가수 1위?", "봄날의 햇살 같은 가수는?",
    "여름 무더위를 날려버릴 목소리는?", "가을 감성에 딱 맞는 목소리는?", "겨울 난로 같은 따뜻한 사람은?",
    "안무 습득력이 가장 빠른 사람은?", "사복 패션 센스가 뛰어난 사람은?", "반려동물을 사랑하는 집사는?",
    "어린 시절 사진과 똑같은 사람은?", "가장 효자/효녀일 것 같은 스타는?", "학창 시절 인기 짱이었을 것 같은?",
    "CF 킹/퀸은 누구?", "유튜브 조회수 대박의 주인공은?", "실시간 검색어를 장악한 스타는?",
    "콘서트 티켓팅이 가장 치열한 가수는?", "팬레터를 가장 많이 받을 것 같은?", "선배 가수들에게 사랑받는 후배는?",
    "후배들을 잘 챙겨주는 든든한 선배는?", "트로트 장르의 벽을 깬 가수는?", "발라드도 잘 부르는 트로트 가수는?",
    "락 스피릿이 충만한 트로트 가수는?", "국악 베이스의 깊은 소리꾼은?", "성악 발성으로 웅장함을 주는?",
    "가장 다재다능한 '부캐' 부자는?", "지역 홍보대사로 활약 중인 사람은?", "기부 천사로 알려진 따뜻한 마음은?",
    "신곡 발표만 하면 대박 나는 믿듣가?", "역주행 신화를 쓴 주인공은?", "오빠/누나 부대를 몰고 다니는?",
    "전국 팔도를 누비는 홍길동은?", "무대 매너 점수 100점 만점!", "엔딩 요정은 바로 나!",
    "카메라 아이컨택이 심쿵인 가수는?", "목소리만 들어도 힐링되는 치유캐?", "인생 2회차 같은 깊은 감성은?",
    "트로트계의 베토벤, 작사/작곡 능력자?", "가장 로맨틱한 보이스는?", "섹시한 매력이 넘치는 스타는?",
    "귀여움 한도 초과인 스타는?", "청량함 그 자체인 인간 사이다!", "분위기 메이커는 누구?",
    "가장 성실하기로 소문난 노력파는?", "연습벌레로 알려진 가수는?", "무명 시절을 딛고 일어선 인간 승리!",
    "지금 이 순간 가장 빛나는 별!", "트로트의 미래를 이끌어갈 주역!", "영원한 우리의 오빠/언니!"
]

# --- [4. 핵심 기능 함수] ---

def fetch_image_secure(url):
    """봇 차단 우회하여 이미지 다운로드"""
    if not url or not url.startswith("http"): return None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    except Exception: return None

def search_image_auto(query):
    """이미지 검색 시도"""
    search_terms = [f"{query} wiki image", f"{query} singer", f"{query} 트로트"]
    try:
        with DDGS() as ddgs:
            for term in search_terms:
                results = list(ddgs.images(term, max_results=1))
                if results: return results[0]['image']
    except Exception: pass
    return None

def convert_to_sketch(pil_image):
    """스케치 필터 강제 적용"""
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
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf"
    try:
        response = requests.get(font_url, timeout=10)
        return BytesIO(response.content)
    except: return None

def create_shorts_image(q_text, names, image_sources):
    canvas = Image.new('RGB', (1080, 1920), (0, 0, 0))
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

    bbox = draw.textbbox((0, 0), q_text, font=font_title)
    text_w = bbox[2] - bbox[0]
    draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill="#FFFF00", align="center")

    positions = [(50, 500), (560, 500), (50, 1100), (560, 1100)]
    size = (470, 550)

    for i, (name, source, pos) in enumerate(zip(names, image_sources, positions)):
        img = None
        # 소스 처리
        if isinstance(source, BytesIO): img = Image.open(source).convert("RGB")
        elif isinstance(source, str): img = fetch_image_secure(source)
        
        # 이미지 가공
        if img:
            img = convert_to_sketch(img) # 스케치 필수
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
        draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=20, fill="black", outline="#00FF00", width=3)
        
        bbox_name = draw.textbbox((0, 0), name, font=font_name)
        name_w = bbox_name[2] - bbox_name[0]
        name_h = bbox_name[3] - bbox_name[1]
        draw.text((tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), name, font=font_name, fill="#00FF00")

    return canvas

# --- [5. 메인 UI] ---
st.title("🛡️ 쇼츠 자동 생성기 (검색 링크 지원)")

tab_singer, tab_topic = st.tabs(["👤 인물 설정", "📝 주제 설정"])

with tab_singer:
    singer_mode = st.radio("인물 선택 방식", ["랜덤 추천", "직접 선택"], horizontal=True, key="s_mode")
    selected_main_singer = None
    if singer_mode == "직접 선택":
        selected_main_singer = st.selectbox("가수 목록", TROT_SINGERS, key="s_select")

with tab_topic:
    topic_mode = st.radio("주제 선택 방식", ["랜덤 추천", "직접 선택"], horizontal=True, key="t_mode")
    selected_quiz_topic = None
    if topic_mode == "직접 선택":
        selected_quiz_topic = st.selectbox("주제 목록", QUIZ_TOPICS, key="t_select")

st.divider()

if st.button("🚀 설정대로 퀴즈 생성하기", type="primary", use_container_width=True):
    with st.spinner("🤖 이미지를 찾는 중입니다..."):
        if singer_mode == "직접 선택": correct_answer = selected_main_singer
        else: correct_answer = random.choice(TROT_SINGERS)
        
        wrong_answers = random.sample([s for s in TROT_SINGERS if s != correct_answer], 3)
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        
        if topic_mode == "직접 선택": question = selected_quiz_topic.format(name=correct_answer)
        else: question = random.choice(QUIZ_TOPICS).format(name=correct_answer)
        
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
        st.subheader("🛠️ 사진 확인 & 업로드")
        new_q = st.text_area("질문 멘트", value=data['q'], height=80)
        final_sources = []
        
        for i in range(4):
            singer_name = data['names'][i]
            st.markdown(f"**{i+1}번: {singer_name}**")
            
            # 1. 자동 검색된 이미지가 있으면 표시
            if data['urls'][i]:
                st.image(data['urls'][i], width=150)
                final_sources.append(data['urls'][i])
            else:
                # 2. 없으면 구글 검색 링크와 업로드 버튼 제공
                st.warning("이미지 자동 로드 실패")
                
                # 구글 이미지 검색 링크 생성
                search_query = urllib.parse.quote(f"{singer_name} 고화질")
                google_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
                st.markdown(f"👉 **[🔍 '{singer_name}' 사진 구글에서 찾기 (클릭)]({google_url})**")
                
                uploaded = st.file_uploader(f"{singer_name} 사진 직접 올리기", key=f"up_{i}")
                final_sources.append(uploaded if uploaded else None)
            st.divider()

    with col_r:
        st.subheader("📸 최종 결과물")
        if st.button("✨ 결과물 다시 그리기", use_container_width=True): pass

        final_img = create_shorts_image(new_q, data['names'], final_sources)
        st.image(final_img, caption="완성본 (자동 스케치 적용됨)", use_container_width=True)
        
        buf = BytesIO()
        final_img.save(buf, format="JPEG", quality=95)
        st.download_button("💾 이미지 다운로드", data=buf.getvalue(), file_name="shorts_final.jpg", mime="image/jpeg", type="primary", use_container_width=True)