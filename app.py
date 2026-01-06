import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# --- [1. 기본 설정 및 폴더 준비] ---
st.set_page_config(page_title="쇼츠 생성기 (최종보완)", page_icon="✨", layout="wide")

IMAGE_SAVE_DIR = "images"
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

FONT_FILE = "NanumGothic-ExtraBold.ttf"

# --- [2. 데이터 설정] ---
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

# --- [3. 핵심 기능 함수] ---

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
    
    font_title = get_font(design['t_size'])
    font_name = get_font(design['n_size'])
    font_bottom = get_font(design['b_size']) # 하단 문구 폰트
    
    # 1. 상단 질문 그리기
    try:
        bbox = draw.textbbox((0, 0), q_text, font=font_title)
        text_w = bbox[2] - bbox[0]
        draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill=design['t_color'], align="center")
    except:
        draw.text((50, 150), q_text, fill=design['t_color'])

    # 2. 이미지 배치 (크기 줄이고 위로 올림)
    # 기존 Y위치: 500, 1100 -> 변경: 450, 1050 (위로 올림)
    positions = [(70, 450), (560, 450), (70, 1050), (560, 1050)]
    # 기존 사이즈: (470, 550) -> 변경: (450, 500) (조금 줄임)
    size = (450, 500)

    for i, (name, pos) in enumerate(zip(names, positions)):
        img = load_image_from_disk(name)
        if img is None:
            img = Image.new('RGB', size, (50, 50, 50))
        
        # 리사이즈
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
        tag_w, tag_h = 380, 110 # 이름표도 살짝 줄임
        tag_x = pos[0] + (size[0] - tag_w) // 2
        tag_y = pos[1] + size[1] - (tag_h // 2)
        
        draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=20, fill=design['tag_bg'], outline=design['border'], width=5)
        
        # 이름
        try:
            bbox_name = draw.textbbox((0, 0), name, font=font_name)
            name_w = bbox_name[2] - bbox_name[0]
            name_h = bbox_name[3] - bbox_name[1]
            draw.text((tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), name, font=font_name, fill=design['n_color'])
        except: pass

    # 3. 하단 문구 그리기 (새로 추가된 영역)
    bottom_text = design.get('bottom_text', '')
    if bottom_text:
        try:
            bbox_b = draw.textbbox((0, 0), bottom_text, font=font_bottom)
            text_bw = bbox_b[2] - bbox_b[0]
            # Y좌표 1750 부근에 배치 (하단 여백 활용)
            draw.text(((1080 - text_bw) / 2, 1750), bottom_text, font=font_bottom, fill=design['t_color'], align="center")
        except: pass

    return canvas

# --- [4. 메인 UI] ---
st.title("✨ 쇼츠 생성기 (최종 보완판)")

if not os.path.exists(FONT_FILE):
    st.error(f"⚠️ '{FONT_FILE}' 파일이 필요합니다.")

# 디자인 설정 (사이드바)
with st.sidebar:
    st.header("🎨 디자인 & 문구")
    
    with st.expander("색상 설정", expanded=False):
        bg_color = st.color_picker("배경색", "#000000")
        t_color = st.color_picker("질문/하단 색", "#FFFF00")
        tag_bg = st.color_picker("이름표 배경", "#000000")
        border = st.color_picker("테두리 색", "#00FF00")
        n_color = st.color_picker("이름 색", "#00FF00")
        
    with st.expander("크기 설정", expanded=True):
        t_size = st.slider("상단 질문 크기", 50, 150, 90)
        n_size = st.slider("이름 크기", 40, 120, 65)
        b_size = st.slider("하단 문구 크기", 30, 100, 50) # 하단 크기 추가

    st.divider()
    st.header("📝 하단 문구")
    bottom_text_input = st.text_area("하단에 들어갈 문구를 입력하세요", "구독과 좋아요는 사랑입니다💖\n댓글로 정답을 남겨주세요!")
    
    design = {
        'bg': bg_color, 't_color': t_color, 'tag_bg': tag_bg, 'border': border, 'n_color': n_color,
        't_size': t_size, 'n_size': n_size, 'b_size': b_size,
        'bottom_text': bottom_text_input # 하단 문구 저장
    }

# 탭 구성
tab_manage, tab_create = st.tabs(["1. 📸 사진 등록/관리", "2. 🚀 퀴즈 만들기"])

# [탭 1: 사진 등록] (기존과 동일)
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
        # 가수 선정
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
        
        # 질문 선정
        winner = random.choice(options)
        question = (sel_topic if q_mode == "직접" else random.choice(QUIZ_TOPICS)).format(name=winner)
        
        # 상태 저장 (중요: 현재 가수 명단을 저장해야 수정 반영 가능)
        st.session_state['current_options'] = options
        st.session_state['last_q'] = question
        # 이미지 최초 생성
        st.session_state['result_img'] = create_final_image(question, options, design)

    # 결과 화면
    if 'result_img' in st.session_state:
        col_res1, col_res2 = st.columns([1, 1.2])
        with col_res1:
            st.info("Tip: 사이드바에서 디자인과 하단 문구를 수정할 수 있습니다.")
            # 상단 멘트 수정 입력창
            new_q_val = st.text_area("상단 질문 멘트 수정", value=st.session_state.get('last_q', ''))
            
        with col_res2:
            # === [핵심 수정] 수정사항 반영 버튼 ===
            if st.button("✨ 디자인/멘트 수정사항 반영", type="primary", use_container_width=True):
                # 저장된 가수 명단이 있을 때만 실행
                if 'current_options' in st.session_state:
                    # 입력된 새 멘트와 현재 사이드바 디자인 설정으로 다시 그리기
                    st.session_state['result_img'] = create_final_image(new_q_val, st.session_state['current_options'], design)
                    st.session_state['last_q'] = new_q_val # 수정된 멘트 저장
                    st.rerun() # 즉시 반영

            st.image(st.session_state['result_img'], caption="최종 결과물", use_container_width=True)
            buf = BytesIO()
            st.session_state['result_img'].save(buf, format="JPEG", quality=100)
            st.download_button("💾 이미지 다운로드", buf.getvalue(), "shorts_final.jpg", "image/jpeg", type="primary", use_container_width=True)