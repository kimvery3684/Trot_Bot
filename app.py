import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# --- [1. 기본 설정 및 폴더 준비] ---
st.set_page_config(page_title="쇼츠 생성기 (대본추가)", page_icon="🎙️", layout="wide")

IMAGE_SAVE_DIR = "images"
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

FONT_FILE = "NanumGothic-ExtraBold.ttf"

# --- [2. 비밀번호 보안] ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.warning("🔒 접속하려면 비밀번호가 필요합니다.")
        password_input = st.text_input("비밀번호", type="password")
        CORRECT_PASSWORD = st.secrets["APP_PASSWORD"] if "APP_PASSWORD" in st.secrets else "1234"
        if password_input:
            if password_input == CORRECT_PASSWORD:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
    return False

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

# --- [4. 핵심 기능 함수] ---

def save_image_to_disk(singer_name, uploaded_file):
    try:
        img = Image.open(uploaded_file).convert("RGB")
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{singer_name}.jpg")
        img.save(file_path, "JPEG", quality=100)
        return True
    except Exception as e:
        st.error(f"저장 실패: {e}")
        return False

def load_image_from_disk(singer_name):
    for ext in ['jpg', 'jpeg', 'png', 'JPG', 'PNG']:
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{singer_name}.{ext}")
        if os.path.exists(file_path):
            try:
                return Image.open(file_path).convert("RGB")
            except: pass
    return None

def get_font(size):
    if os.path.exists(FONT_FILE):
        return ImageFont.truetype(FONT_FILE, size)
    else:
        return ImageFont.load_default()

def create_final_image(q_text, names, design):
    canvas = Image.new('RGB', (1080, 1920), design['bg'])
    draw = ImageDraw.Draw(canvas)
    
    font_title = get_font(design['top_size'])
    font_name = get_font(design['n_size'])
    font_bottom = get_font(design['bot_size'])
    
    # 1. 상단 질문
    top_y = design['layout_top_y']
    try:
        bbox = draw.textbbox((0, 0), q_text, font=font_title)
        text_w = bbox[2] - bbox[0]
        draw.text(((1080 - text_w) / 2, top_y), q_text, font=font_title, fill=design['top_color'], align="center")
    except:
        draw.text((50, top_y), q_text, fill=design['top_color'])

    # 2. 이미지 배치
    img_w = design['layout_img_w']
    img_h = int(img_w * 1.1)
    start_y = design['layout_img_y']
    gap = 40 
    total_w = (img_w * 2) + gap
    start_x = (1080 - total_w) // 2

    positions = [
        (start_x, start_y), (start_x + img_w + gap, start_y), 
        (start_x, start_y + img_h + gap), (start_x + img_w + gap, start_y + img_h + gap)
    ]
    size = (img_w, img_h)

    for i, (name, pos) in enumerate(zip(names, positions)):
        img = load_image_from_disk(name)
        if img is None:
            img = Image.new('RGB', size, (50, 50, 50))
        
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
        tag_w = int(img_w * 0.9)
        tag_h = 110
        tag_x = pos[0] + (size[0] - tag_w) // 2
        tag_y = pos[1] + size[1] - (tag_h // 2)
        draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=20, fill=design['tag_bg'], outline=design['border'], width=5)
        
        display_name = f"{i+1}  {name}"
        try:
            bbox_name = draw.textbbox((0, 0), display_name, font=font_name)
            name_w = bbox_name[2] - bbox_name[0]
            name_h = bbox_name[3] - bbox_name[1]
            draw.text((tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), display_name, font=font_name, fill=design['n_color'])
        except: 
            draw.text((tag_x+20, tag_y+30), display_name, fill=design['n_color'])

    # 3. 하단 문구
    bottom_text = design.get('bottom_text', '')
    bot_y = design['layout_bot_y']
    if bottom_text:
        try:
            bbox_b = draw.textbbox((0, 0), bottom_text, font=font_bottom)
            text_bw = bbox_b[2] - bbox_b[0]
            draw.text(((1080 - text_bw) / 2, bot_y), bottom_text, font=font_bottom, fill=design['bot_color'], align="center")
        except: pass

    return canvas

# --- [5. 콘텐츠 생성 함수 (메타데이터 + 대본)] ---
def generate_youtube_metadata(question, singers):
    # 제목/설명/태그
    titles = [
        f"🔥 {question} 1위는 과연 누구일까요? #트로트",
        f"대박 반전! 😲 {question} 투표 결과는? #{singers[0]} #{singers[1]}",
        f"당신의 선택은? 👉 {question} (솔직히 이분이죠)",
        f"🏆 트로트 팬들이 뽑은 {question} 레전드 결과"
    ]
    title = random.choice(titles)

    desc = f"""{question}

👇 여러분의 생각을 댓글로 남겨주세요! 👇
(화면을 두 번 터치하면 투표가 완료됩니다 💖)

1️⃣ {singers[0]}
2️⃣ {singers[1]}
3️⃣ {singers[2]}
4️⃣ {singers[3]}

🔥 매일 재밌는 트로트 투표가 올라옵니다! '구독'과 '좋아요' 부탁드려요!

#트로트 #트로트가수 #인기투표 #임영웅 #이찬원 #김호중 #박지현 #{singers[0]} #{singers[1]}
"""
    base_tags = "트로트, 트로트가수, 미스터트롯, 현역가왕, 미스트롯, 인기투표, shorts, 쇼츠, 랭킹"
    singer_tags = ", ".join(singers)
    tags = f"{base_tags}, {singer_tags}, {question.replace(' ','')}"
    return title, desc, tags

def generate_narration_script(question, singers):
    # 30초 분량 쇼츠 대본
    script = f"""(오프닝 - 긴장감 있는 톤으로)
"자, 팬 여러분 주목하세요! 오늘의 난제, {question} 과연 누구일까요?"

(본문 - 빠르고 경쾌하게)
"후보 1번! 믿고 듣는 감성 장인, {singers[0]}!
후보 2번! 무대 위의 카리스마, {singers[1]}!
후보 3번! 트로트계의 보석, {singers[2]}!
마지막 후보 4번! 떠오르는 대세, {singers[3]}!"

(클로징 - 호소력 있게)
"와... 진짜 고르기 힘든데요? 
여러분의 최애 가수를 지금 바로 댓글로 적어주세요! 
좋아요는 사랑입니다!"
"""
    return script

# --- [6. 메인 UI] ---
st.title("🎙️ 쇼츠 생성기 (대본 추가)")

if not os.path.exists(FONT_FILE):
    st.error(f"⚠️ '{FONT_FILE}' 파일이 필요합니다.")

# 디자인 설정 (사이드바)
with st.sidebar:
    st.header("🎨 디자인 & 레이아웃")
    tab_color, tab_layout, tab_text = st.tabs(["색상/크기", "위치/배치", "문구"])
    
    with tab_color:
        st.subheader("🖍️ 색상 설정")
        bg_color = st.color_picker("배경색", "#000000")
        top_color = st.color_picker("⬆️ 상단 질문 색", "#FFFF00")
        bot_color = st.color_picker("⬇️ 하단 문구 색", "#FFFFFF")
        st.divider()
        tag_bg = st.color_picker("이름표 배경", "#000000")
        border = st.color_picker("테두리 색", "#00FF00")
        n_color = st.color_picker("이름 색", "#00FF00")
        st.divider()
        st.subheader("📏 크기 설정")
        top_size = st.slider("⬆️ 상단 질문 크기", 50, 150, 90)
        bot_size = st.slider("⬇️ 하단 문구 크기", 30, 120, 70)
        n_size = st.slider("이름 크기", 40, 120, 65)

    with tab_layout:
        st.info("💡 화면 배치를 조절하세요")
        layout_top_y = st.slider("상단 질문 위치 (Y)", 50, 500, 150)
        st.divider()
        layout_img_w = st.slider("사진 크기 (너비)", 300, 500, 420)
        layout_img_y = st.slider("사진 뭉치 위치 (Y)", 200, 1000, 420)
        st.divider()
        layout_bot_y = st.slider("하단 문구 위치 (Y)", 1200, 1850, 1600)

    with tab_text:
        bottom_text_input = st.text_area("하단 문구 내용", "화면 두번 터치\n댓글로 정답을 남겨주세요!")
    
    design = {
        'bg': bg_color, 'top_color': top_color, 'top_size': top_size, 
        'bot_color': bot_color, 'bot_size': bot_size, 'tag_bg': tag_bg, 'border': border, 
        'n_color': n_color, 'n_size': n_size, 'bottom_text': bottom_text_input,
        'layout_top_y': layout_top_y, 'layout_img_w': layout_img_w, 
        'layout_img_y': layout_img_y, 'layout_bot_y': layout_bot_y
    }

# 탭 구성
tab_manage, tab_create = st.tabs(["1. 📸 사진 등록/관리", "2. 🚀 퀴즈 만들기"])

# [탭 1: 사진 등록]
with tab_manage:
    st.subheader("가수 사진 영구 저장")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        target = st.selectbox("가수 선택", TROT_SINGERS_TOP50)
        up_file = st.file_uploader(f"'{target}' 사진 업로드", type=["jpg", "png", "jpeg"])
        if up_file and st.button("💾 저장하기", type="primary"):
            if save_image_to_disk(target, up_file):
                st.success("저장 완료!")
                st.rerun()
    with col_m2:
        saved = load_image_from_disk(target)
        if saved: st.image(saved, width=200, caption=f"저장된 {target} 사진")
        else: st.warning("저장된 사진이 없습니다.")

# [탭 2: 퀴즈 만들기]
with tab_create:
    st.subheader("퀴즈 생성")
    c1, c2 = st.columns(2)
    with c1:
        mode = st.radio("가수 구성", ["랜덤", "직접 (최대 4명)"], horizontal=True)
        sel_singers = st.multiselect("가수 선택", TROT_SINGERS_TOP50, max_selections=4) if mode == "직접 (최대 4명)" else []
    with c2:
        q_mode = st.radio("질문 선택", ["랜덤", "직접"], horizontal=True)
        sel_topic = st.selectbox("주제 선택", QUIZ_TOPICS) if q_mode == "직접" else None

    if st.button("🚀 퀴즈 이미지 생성", type="primary", use_container_width=True):
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
        
        winner = random.choice(options)
        question = (sel_topic if q_mode == "직접" else random.choice(QUIZ_TOPICS)).format(name=winner)
        
        st.session_state['current_options'] = options
        st.session_state['last_q'] = question
        st.session_state['result_img'] = create_final_image(question, options, design)

    if 'result_img' in st.session_state:
        col_res1, col_res2 = st.columns([1, 1.2])
        
        # === [유튜브 업로드용 탭 구성] ===
        with col_res1:
            st.markdown("### 🔥 유튜브 업로드 센터")
            # 탭 분리: 메타데이터 / 대본
            tab_meta, tab_script = st.tabs(["📝 제목/설명", "🎙️ 나레이션 대본"])
            
            curr_q = st.session_state.get('last_q', '')
            curr_opts = st.session_state.get('current_options', [])
            
            if curr_q and curr_opts:
                meta_title, meta_desc, meta_tags = generate_youtube_metadata(curr_q, curr_opts)
                script_text = generate_narration_script(curr_q, curr_opts)
                
                with tab_meta:
                    st.text_input("📌 제목", value=meta_title)
                    st.text_area("📝 설명", value=meta_desc, height=200)
                    st.text_area("🏷️ 태그", value=meta_tags, height=100)
                
                with tab_script:
                    st.info("쇼츠 영상 길이에 딱 맞는 30초 대본입니다.")
                    st.text_area("대본 내용 (TTS/녹음용)", value=script_text, height=300)
            else:
                st.info("퀴즈 이미지를 먼저 생성해주세요.")

            st.divider()
            new_q_val = st.text_area("이미지 상단 질문 수정", value=curr_q)
            
        with col_res2:
            if st.button("✨ 디자인/멘트 수정사항 반영", type="primary", use_container_width=True):
                if 'current_options' in st.session_state:
                    st.session_state['result_img'] = create_final_image(new_q_val, st.session_state['current_options'], design)
                    st.session_state['last_q'] = new_q_val
                    st.rerun()

            st.image(st.session_state['result_img'], caption="최종 결과물", use_container_width=True)
            buf = BytesIO()
            st.session_state['result_img'].save(buf, format="JPEG", quality=100)
            st.download_button("💾 이미지 다운로드", buf.getvalue(), "shorts_final.jpg", "image/jpeg", type="primary", use_container_width=True)