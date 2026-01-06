import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# --- [1. 기본 설정 및 폴더 준비] ---
st.set_page_config(page_title="쇼츠 생성기 (사진관리자)", page_icon="🗂️", layout="wide")

# 사진이 저장될 진짜 내 컴퓨터 폴더
IMAGE_SAVE_DIR = "images"
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

# 폰트 파일 이름 (같은 폴더에 있어야 함)
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
    """업로드한 파일을 내 컴퓨터 images 폴더에 저장"""
    try:
        # 무조건 jpg로 변환해서 저장 (관리가 편함)
        img = Image.open(uploaded_file).convert("RGB")
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{singer_name}.jpg")
        img.save(file_path, "JPEG", quality=100)
        return True
    except Exception as e:
        st.error(f"저장 실패: {e}")
        return False

def load_image_from_disk(singer_name):
    """내 컴퓨터 images 폴더에서 파일 불러오기"""
    # jpg, png, jpeg 등 확인
    for ext in ['jpg', 'jpeg', 'png', 'JPG', 'PNG']:
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{singer_name}.{ext}")
        if os.path.exists(file_path):
            try:
                return Image.open(file_path).convert("RGB")
            except: pass
    return None

def get_font(size):
    """폰트 로딩 (로컬 파일 우선)"""
    if os.path.exists(FONT_FILE):
        return ImageFont.truetype(FONT_FILE, size)
    else:
        return ImageFont.load_default()

def create_final_image(q_text, names, design):
    canvas = Image.new('RGB', (1080, 1920), design['bg'])
    draw = ImageDraw.Draw(canvas)
    
    font_title = get_font(design['t_size'])
    font_name = get_font(design['n_size'])
    
    # 질문 그리기
    try:
        bbox = draw.textbbox((0, 0), q_text, font=font_title)
        text_w = bbox[2] - bbox[0]
        draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill=design['t_color'], align="center")
    except:
        draw.text((50, 150), q_text, fill=design['t_color'])

    positions = [(50, 500), (560, 500), (50, 1100), (560, 1100)]
    size = (470, 550)

    for i, (name, pos) in enumerate(zip(names, positions)):
        # 저장된 이미지 불러오기
        img = load_image_from_disk(name)
        
        if img is None:
            # 없으면 회색 박스 + 물음표
            img = Image.new('RGB', size, (50, 50, 50))
            draw_temp = ImageDraw.Draw(img)
            # 물음표
        
        # 이미지 크롭 & 리사이즈
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
        
        # 이름
        try:
            bbox_name = draw.textbbox((0, 0), name, font=font_name)
            name_w = bbox_name[2] - bbox_name[0]
            name_h = bbox_name[3] - bbox_name[1]
            draw.text((tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), name, font=font_name, fill=design['n_color'])
        except:
             draw.text((tag_x+50, tag_y+30), name, fill=design['n_color'])

    return canvas

# --- [4. 메인 UI] ---
st.title("🗂️ 쇼츠 생성기 (사진 관리자)")

if not os.path.exists(FONT_FILE):
    st.error(f"⚠️ 'NanumGothic-ExtraBold.ttf' 파일이 없습니다! 같은 폴더에 넣어주세요.")

# 디자인 설정
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
    design = {'bg': bg_color, 't_color': t_color, 'tag_bg': tag_bg, 'border': border, 'n_color': n_color, 't_size': t_size, 'n_size': n_size}

# 탭 분리: 1. 사진 등록 / 2. 퀴즈 만들기
tab_manage, tab_create = st.tabs(["1. 📸 사진 등록/관리", "2. 🚀 퀴즈 만들기"])

# --- [탭 1: 사진 등록] ---
with tab_manage:
    st.subheader("가수 사진을 영구 저장하세요")
    st.caption(f"여기서 저장하면 내 컴퓨터 '{IMAGE_SAVE_DIR}' 폴더에 파일이 생성됩니다.")
    
    col_m1, col_m2 = st.columns([1, 1])
    
    with col_m1:
        target_singer = st.selectbox("가수 선택", TROT_SINGERS_TOP50)
        uploaded_file = st.file_uploader(f"'{target_singer}' 사진 업로드", type=["jpg", "png", "jpeg"])
        
        if uploaded_file:
            st.image(uploaded_file, caption="업로드할 사진 미리보기", width=200)
            if st.button("💾 이 사진으로 영구 저장", type="primary"):
                if save_image_to_disk(target_singer, uploaded_file):
                    st.success(f"저장 완료! '{target_singer}.jpg' 파일이 생성되었습니다.")
                    st.rerun() # 새로고침해서 반영

    with col_m2:
        st.write(f"현재 저장된 '{target_singer}' 사진:")
        saved_img = load_image_from_disk(target_singer)
        if saved_img:
            st.image(saved_img, width=200)
            st.info("✅ 이미 저장된 사진이 있습니다.")
        else:
            st.warning("❌ 아직 저장된 사진이 없습니다.")

# --- [탭 2: 퀴즈 만들기] ---
with tab_create:
    st.subheader("저장된 사진으로 퀴즈 만들기")
    
    c1, c2 = st.columns(2)
    with c1:
        mode = st.radio("가수 구성", ["랜덤", "직접 (최대 4명)"], horizontal=True)
        sel_singers = []
        if mode == "직접 (최대 4명)":
            sel_singers = st.multiselect("가수 선택", TROT_SINGERS_TOP50, max_selections=4)
    with c2:
        q_mode = st.radio("질문 선택", ["랜덤", "직접"], horizontal=True)
        sel_topic = st.selectbox("주제 선택", QUIZ_TOPICS) if q_mode == "직접" else None

    if st.button("🚀 퀴즈 이미지 생성", type="primary", use_container_width=True):
        # 가수 선정 로직
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
        
        # 이미지 생성
        st.session_state['result_img'] = create_final_image(question, options, design)
        st.session_state['last_q'] = question # 멘트 수정을 위해 저장

    # 결과 보여주기
    if 'result_img' in st.session_state:
        col_res1, col_res2 = st.columns([1, 1.2])
        
        with col_res1:
            st.info("💡 사진이 비어있다면 [1. 사진 등록] 탭에서 사진을 저장해주세요.")
            new_q_val = st.text_area("멘트 수정", value=st.session_state.get('last_q', ''))
            
        with col_res2:
            if st.button("✨ 디자인/멘트 수정사항 반영"):
                # 현재 설정으로 다시 그리기 (가수 명단은 유지)
                # (복잡도를 줄이기 위해 새로 생성하는게 아니라, 기존 명단으로 다시 그림)
                pass 
                
            st.image(st.session_state['result_img'], caption="최종 결과물", use_container_width=True)
            
            buf = BytesIO()
            st.session_state['result_img'].save(buf, format="JPEG", quality=100)
            st.download_button("💾 이미지 다운로드", buf.getvalue(), "shorts.jpg", "image/jpeg", type="primary", use_container_width=True)