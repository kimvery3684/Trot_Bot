import streamlit as st
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import urllib.parse

# --- [기본 설정] ---
st.set_page_config(page_title="쇼츠 이미지 생성기", page_icon="📸", layout="wide")

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
    response = requests.get(font_url)
    return BytesIO(response.content)

# --- [이미지 합성 엔진] ---
def create_shorts_image(q_text, names, image_urls):
    # 1. 검은색 캔버스 생성 (1080x1920 쇼츠 규격)
    canvas = Image.new('RGB', (1080, 1920), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    
    # 폰트 로드
    font_bytes = load_fonts()
    font_title = ImageFont.truetype(font_bytes, 100) # 질문 폰트 크기
    font_name = ImageFont.truetype(font_bytes, 70)   # 이름 폰트 크기

    # 2. 질문 그리기 (상단 중앙)
    # 텍스트 중앙 정렬 계산
    bbox = draw.textbbox((0, 0), q_text, font=font_title)
    text_w = bbox[2] - bbox[0]
    draw.text(((1080 - text_w) / 2, 150), q_text, font=font_title, fill="#FFFF00", align="center")

    # 3. 4분할 그리드 좌표 설정
    # (x, y) 좌표: [왼쪽위, 오른쪽위, 왼쪽아래, 오른쪽아래]
    positions = [(50, 500), (560, 500), (50, 1100), (560, 1100)]
    size = (470, 550) # 각 사진 크기

    for i, (name, url, pos) in enumerate(zip(names, image_urls, positions)):
        # 이미지 다운로드 및 붙여넣기
        try:
            if url:
                response = requests.get(url, timeout=3)
                img = Image.open(BytesIO(response.content)).convert("RGB")
                img = img.resize(size) # 크기 맞추기
            else:
                # URL 없으면 회색 박스
                img = Image.new('RGB', size, (50, 50, 50))
        except:
            # 에러나면 빨간 박스
            img = Image.new('RGB', size, (50, 0, 0))

        # 캔버스에 붙여넣기
        canvas.paste(img, pos)

        # 4. 이름표 만들기 (검은 배경 + 초록 글씨)
        # 이름표 배경 박스 그리기
        tag_w, tag_h = 300, 120
        tag_x = pos[0] + (size[0] - tag_w) // 2
        tag_y = pos[1] + size[1] - (tag_h // 2) # 사진 하단에 걸치게
        
        # 둥근 사각형
        draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=20, fill="black", outline="#00FF00", width=3)
        
        # 이름 쓰기
        bbox_name = draw.textbbox((0, 0), name, font=font_name)
        name_w = bbox_name[2] - bbox_name[0]
        name_h = bbox_name[3] - bbox_name[1]
        draw.text((tag_x + (tag_w - name_w) / 2, tag_y + (tag_h - name_h) / 2 - 10), name, font=font_name, fill="#00FF00")

    return canvas

# --- [메인 UI] ---
st.title("📸 쇼츠 이미지 자동 생성기")
st.markdown("사진 URL만 넣으면 **쇼츠 규격(9:16) 이미지 파일**을 만들어줍니다!")

# 1. 데이터 생성 파트
if st.button("🎲 1. 가수 랜덤 뽑기", type="primary", use_container_width=True):
    correct_answer = random.choice(TROT_SINGERS)
    wrong_answers = random.sample([s for s in TROT_SINGERS if s != correct_answer], 3)
    options = wrong_answers + [correct_answer]
    random.shuffle(options)
    question = random.choice(QUIZ_TEMPLATES).format(name=correct_answer)
    
    st.session_state['gen_data'] = {
        'q': question,
        'names': options,
        'urls': ["", "", "", ""] # 초기 URL은 비어있음
    }

# 2. 편집 파트
if 'gen_data' in st.session_state:
    data = st.session_state['gen_data']
    
    col_l, col_r = st.columns([1, 1.2])
    
    with col_l:
        st.subheader("📝 내용 편집")
        new_q = st.text_area("질문 멘트", value=data['q'], height=100)
        
        # 4명 가수 입력창 생성
        new_urls = []
        new_names = []
        
        for i in range(4):
            st.markdown(f"**{i+1}번 가수: {data['names'][i]}**")
            # 검색 버튼
            search_url = f"https://www.google.com/search?tbm=isch&q=가수+{urllib.parse.quote(data['names'][i])}+고화질"
            st.markdown(f"[🔍 구글에서 사진 찾기 (클릭)]({search_url})")
            
            # 입력창
            input_url = st.text_input(f"{i+1}번 사진 주소 (URL) 붙여넣기", key=f"url_{i}", placeholder="이미지 우클릭 -> 이미지 주소 복사")
            new_urls.append(input_url)
            new_names.append(data['names'][i])
            st.divider()

    with col_r:
        st.subheader("🖼️ 결과 미리보기")
        if st.button("✨ 이미지 생성하기 (Click)", type="primary"):
            # 이미지 생성 로직 실행
            with st.spinner("이미지 합성 중..."):
                final_img = create_shorts_image(new_q, new_names, new_urls)
                
                # 화면에 표시
                st.image(final_img, caption="완성된 쇼츠 이미지", use_container_width=True)
                
                # 다운로드 버튼 생성
                buf = BytesIO()
                final_img.save(buf, format="JPEG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="💾 이미지 다운로드 (Download)",
                    data=byte_im,
                    file_name="trot_shorts_quiz.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )