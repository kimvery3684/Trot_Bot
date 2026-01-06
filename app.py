import streamlit as st
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import urllib.parse

# --- [기본 설정] ---
st.set_page_config(page_title="쇼츠 이미지 생성기 (최종)", page_icon="📸", layout="wide")

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

# --- [폰트 로드 함수 (한글 깨짐 방지)] ---
@st.cache_resource
def load_fonts():
    # 나눔고딕 폰트 다운로드 (클라우드 환경용)
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-ExtraBold.ttf"
    try:
        response = requests.get(font_url, timeout=5)
        return BytesIO(response.content)
    except:
        st.error("폰트 다운로드 실패. 기본 폰트가 사용될 수 있습니다.")
        return None

# --- [이미지 합성 엔진 (업그레이드됨)] ---
def create_shorts_image(q_text, names, uploaded_files):
    # 1. 검은색 캔버스 생성 (1080x1920 쇼츠 규격)
    canvas = Image.new('RGB', (1080, 1920), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    # 폰트 로드
    font_bytes = load_fonts()
    if font_bytes:
        font_title = ImageFont.truetype(font_bytes, 100) # 질문 폰트 크기
        font_name = ImageFont.truetype(font_bytes, 70)   # 이름 폰트 크기
    else:
        font_title = ImageFont.load_default()
        font_name = ImageFont.load_default()

    # 2. 질문 그리기 (상단 중앙)
    bbox = draw.textbbox((0, 0), q_text, font=font_title)
    text_w = bbox[2] - bbox[0]
    draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill="#FFFF00", align="center")

    # 3. 4분할 그리드 좌표 설정
    positions = [(50, 500), (560, 500), (50, 1100), (560, 1100)]
    size = (470, 550) # 각 사진 크기

    for i, (name, uploaded_file, pos) in enumerate(zip(names, uploaded_files, positions)):
        # --- [핵심 변경점] 업로드된 파일 처리 ---
        try:
            if uploaded_file is not None:
                # 업로드된 파일을 이미지로 열기
                img = Image.open(uploaded_file).convert("RGB")
                # 비율 유지하며 자르기 (Center Crop)
                img_ratio = img.width / img.height
                target_ratio = size[0] / size[1]
                
                if img_ratio > target_ratio: # 이미지가 더 넓은 경우
                    new_width = int(img.height * target_ratio)
                    offset = (img.width - new_width) // 2
                    img = img.crop((offset, 0, offset + new_width, img.height))
                else: # 이미지가 더 긴 경우
                    new_height = int(img.width / target_ratio)
                    offset = (img.height - new_height) // 2
                    img = img.crop((0, offset, img.width, offset + new_height))
                    
                img = img.resize(size, Image.LANCZOS) # 최종 크기 맞추기
            else:
                # 파일 없으면 회색 박스
                img = Image.new('RGB', size, (50, 50, 50))
                draw_temp = ImageDraw.Draw(img)
                draw_temp.text((100, 250), "사진 없음", fill="white", font=font_name)
        except Exception as e:
            # 에러나면 빨간 박스
            img = Image.new('RGB', size, (50, 0, 0))
            print(f"이미지 처리 오류: {e}")

        # 캔버스에 붙여넣기
        canvas.paste(img, pos)

        # 4. 이름표 만들기 (검은 배경 + 초록 글씨)
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
st.title("📸 쇼츠 이미지 생성기 (첨부/붙여넣기 Ver.)")
st.markdown("이제 사진 파일을 직접 **드래그 앤 드롭** 하거나 **붙여넣기(Ctrl+V)** 하세요!")

# 1. 데이터 생성 파트
if st.button("🎲 1. 가수 랜덤 뽑기 (시작)", type="primary", use_container_width=True):
    correct_answer = random.choice(TROT_SINGERS)
    wrong_answers = random.sample([s for s in TROT_SINGERS if s != correct_answer], 3)
    options = wrong_answers + [correct_answer]
    random.shuffle(options)
    question = random.choice(QUIZ_TEMPLATES).format(name=correct_answer)
    
    st.session_state['gen_data'] = {
        'q': question,
        'names': options
    }

# 2. 편집 파트
if 'gen_data' in st.session_state:
    data = st.session_state['gen_data']
    
    col_l, col_r = st.columns([1.2, 1])
    
    with col_l:
        st.subheader("📝 사진 업로드 및 편집")
        st.info("💡 팁: 구글에서 이미지를 복사한 후, 아래 박스를 클릭하고 Ctrl+V를 누르면 바로 붙여넣기 됩니다!")
        new_q = st.text_area("질문 멘트 수정", value=data['q'], height=80)
        
        uploaded_files = []
        new_names = []
        
        for i in range(4):
            st.markdown(f"---")
            c1, c2 = st.columns([1, 2])
            with c1:
                 st.markdown(f"### {i+1}번 가수")
                 # 이름 수정 기능 추가
                 name_input = st.text_input(f"{i+1}번 이름", value=data['names'][i], key=f"name_{i}", label_visibility="collapsed")
                 new_names.append(name_input)
                 
                 # 구글 검색 링크
                 search_url = f"https://www.google.com/search?tbm=isch&q=가수+{urllib.parse.quote(name_input)}+고화질"
                 st.markdown(f"[👉 {name_input} 사진 검색하기]({search_url})")

            with c2:
                # --- [핵심] 파일 업로더 위젯 ---
                uploaded = st.file_uploader(
                    f"📸 {i+1}번 사진을 여기에 넣으세요", 
                    type=["jpg", "png", "jpeg", "webp"], 
                    key=f"upload_{i}"
                )
                uploaded_files.append(uploaded)

    with col_r:
        st.subheader("🖼️ 결과 미리보기 및 다운로드")
        # 4장이 모두 업로드되지 않아도 생성은 되게 함
        if st.button("✨ 이미지 합성하기 (Click)", type="primary", use_container_width=True):
            with st.spinner("열심히 합성 중입니다... 잠시만요!"):
                # 이미지 생성 함수 호출
                final_img = create_shorts_image(new_q, new_names, uploaded_files)
                
                # 화면에 보여주기
                st.image(final_img, caption="완성된 쇼츠 이미지 (9:16)", use_container_width=True)
                
                # 다운로드 버튼 준비
                buf = BytesIO()
                final_img.save(buf, format="JPEG", quality=95)
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="💾 완성된 이미지 다운로드 (Click)",
                    data=byte_im,
                    file_name=f"trot_shorts_{random.randint(100,999)}.jpg",
                    mime="image/jpeg",
                    use_container_width=True,
                    type="primary"
                )
else:
    st.info("👈 먼저 '가수 랜덤 뽑기' 버튼을 눌러주세요.")