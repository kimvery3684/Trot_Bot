import streamlit as st
import random
import urllib.parse

# --- [기본 설정] ---
st.set_page_config(page_title="트로트 쇼츠 메이커 (Design Pro)", page_icon="🎨", layout="wide")

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

# --- [데이터] ---
TROT_SINGERS = ["임영웅","영탁","이찬원","김호중","정동원","장민호","김희재","나훈아","남진","송가인","장윤정","홍진영","박군","박서진","진성","설운도","태진아","송대관","김연자","주현미","양지은","전유진","안성훈","박지현","손태진","에녹","신성","민수현","김다현","김태연","요요미","마이진","린","박구윤","신유","금잔디","조항조","강진","김수희","하춘화","현숙","문희옥","김혜연","진해성","홍지윤","황영웅","공훈","김중연","박민수","나상도","최수호","진욱","박성온","정서주","배아현","오유진","미스김","나영","김소연","정슬","박주희","김수찬","나태주","강혜연","윤수현","조정민","설하윤","류지광","김경민","남승민","황윤성","강태관","김나희","정미애","홍자","정다경","은가은","별사랑","김의영","황민호","황민우","이대원","신인선","노지훈","양지원","한강","재하","신승태","최우진","성리","추혁진","박상철","서주경","한혜진","유지나","김용필","조명섭"]
QUIZ_TEMPLATES = ["다음 중 '{name}' 님은 누구일까요?", "'{name}' 님의 사진을 찾아보세요!", "가수 '{name}' 님은 몇 번일까요?"]

# ==============================================================================
# [사이드바] 디자인 & 컨트롤 패널
# ==============================================================================
with st.sidebar:
    st.title("🎨 디자인 설정")
    st.info("원하는 색상으로 화면을 꾸며보세요!")
    
    # 1. 색상 선택기 (기본값: 요청하신 블랙/옐로우 테마)
    bg_color = st.color_picker("🎨 배경색 (전체)", "#000000")
    top_text_color = st.color_picker("⬆️ 위 글자색 (질문)", "#FFFF00")
    name_text_color = st.color_picker("🅰️ 이름 글자색 (박스 안)", "#FFFFFF")
    bottom_text_color = st.color_picker("⬇️ 아래 글자색 (대본)", "#00FF00")

    st.divider()
    st.subheader("⚙️ 퀴즈 컨트롤")
    generate_btn = st.button("🎲 새 퀴즈 뽑기 (Click)", type="primary", use_container_width=True)

# ==============================================================================
# [CSS 스타일 동적 적용]
# ==============================================================================
st.markdown(f"""
<style>
    /* 전체 배경색 적용 */
    .stApp {{ background-color: {bg_color}; }}
    
    /* 상단 질문 텍스트 스타일 */
    .question-header {{
        color: {top_text_color} !important;
        font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}

    /* 4분할 박스 스타일 (노란 테두리 박스) */
    .choice-box {{
        border: 3px solid #FFEB3B; /* 노란색 테두리 고정 */
        border-radius: 15px; padding: 15px; text-align: center;
        background-color: rgba(255, 255, 0, 0.1); /* 아주 연한 노란 배경 */
        margin-bottom: 15px;
    }}

    /* 박스 안의 이름 텍스트 스타일 */
    .singer-name {{
        color: {name_text_color} !important;
        font-size: 1.8rem; font-weight: bold; margin: 10px 0;
        display: block;
    }}

    /* 사진 자리 표시용 스타일 */
    .photo-placeholder {{
        width: 100%; height: 200px; background-color: #333; color: #ddd;
        display: flex; justify-content: center; align-items: center;
        font-size: 1.2rem; border-radius: 10px; border: 2px dashed #555;
        cursor: pointer; text-decoration: none;
    }}
    .photo-placeholder:hover {{ background-color: #444; border-color: #888; color: #fff; }}

    /* 하단 대본 박스 스타일 */
    .script-box {{
        background-color: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 20px;
        border-left: 5px solid {bottom_text_color};
    }}
    .script-text {{
        color: {bottom_text_color} !important; font-size: 1.1rem; white-space: pre-wrap; line-height: 1.6;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# [메인 로직] 퀴즈 생성 및 데이터 관리
# ==============================================================================
if generate_btn:
    # 1. 랜덤 데이터 생성
    correct_answer = random.choice(TROT_SINGERS)
    wrong_answers = random.sample([s for s in TROT_SINGERS if s != correct_answer], 3)
    options = wrong_answers + [correct_answer]
    random.shuffle(options)
    question_initial = random.choice(QUIZ_TEMPLATES).format(name=correct_answer)
    
    # 2. 세션 상태 초기화 (새로 뽑을 때마다 입력창 리셋)
    st.session_state.update({
        'generated': True, 'q_draft': question_initial, 'answer_real': correct_answer,
        'opt1_draft': options[0], 'opt2_draft': options[1],
        'opt3_draft': options[2], 'opt4_draft': options[3]
    })

# ==============================================================================
# [메인 화면] 레이아웃 구성
# ==============================================================================
if st.session_state.get('generated'):
    # 1. 상단 질문 영역 (수정 가능)
    st.markdown(f'<p class="question-header">{st.session_state["q_draft"]}</p>', unsafe_allow_html=True)
    final_q = st.text_input("🔻 질문 멘트 수정 (안 보이면 아래 화살표 클릭)", value=st.session_state['q_draft'], key="q_edit", label_visibility="collapsed")

    st.write("") # 간격 띄우기

    # 2. 4분할 메인 영역 (2x2 그리드)
    col1, col2 = st.columns(2)
    with col1:
        # 보기 1번
        opt1_val = st.text_input("1번 이름 수정", value=st.session_state['opt1_draft'], key="opt1_edit")
        st.markdown(f"""<div class="choice-box"><span class="singer-name">1. {opt1_val}</span><a href="https://www.google.com/search?tbm=isch&q=트로트가수+{urllib.parse.quote(opt1_val)}+고화질" target="_blank" class="photo-placeholder">📸 사진 검색하기 (클릭)<br>여기에 사진을 배치하세요</a></div>""", unsafe_allow_html=True)
        # 보기 3번
        opt3_val = st.text_input("3번 이름 수정", value=st.session_state['opt3_draft'], key="opt3_edit")
        st.markdown(f"""<div class="choice-box"><span class="singer-name">3. {opt3_val}</span><a href="https://www.google.com/search?tbm=isch&q=트로트가수+{urllib.parse.quote(opt3_val)}+고화질" target="_blank" class="photo-placeholder">📸 사진 검색하기 (클릭)<br>여기에 사진을 배치하세요</a></div>""", unsafe_allow_html=True)

    with col2:
        # 보기 2번
        opt2_val = st.text_input("2번 이름 수정", value=st.session_state['opt2_draft'], key="opt2_edit")
        st.markdown(f"""<div class="choice-box"><span class="singer-name">2. {opt2_val}</span><a href="https://www.google.com/search?tbm=isch&q=트로트가수+{urllib.parse.quote(opt2_val)}+고화질" target="_blank" class="photo-placeholder">📸 사진 검색하기 (클릭)<br>여기에 사진을 배치하세요</a></div>""", unsafe_allow_html=True)
        # 보기 4번
        opt4_val = st.text_input("4번 이름 수정", value=st.session_state['opt4_draft'], key="opt4_edit")
        st.markdown(f"""<div class="choice-box"><span class="singer-name">4. {opt4_val}</span><a href="https://www.google.com/search?tbm=isch&q=트로트가수+{urllib.parse.quote(opt4_val)}+고화질" target="_blank" class="photo-placeholder">📸 사진 검색하기 (클릭)<br>여기에 사진을 배치하세요</a></div>""", unsafe_allow_html=True)

    st.divider()

    # 3. 하단 대본 영역
    st.subheader("📜 성우 대본 (색상 적용됨)")
    current_options = [opt1_val, opt2_val, opt3_val, opt4_val]
    real_ans = st.session_state['answer_real']
    try:
        ans_idx = current_options.index(real_ans) + 1
        final_answer_text = real_ans
    except ValueError:
        ans_idx = "?"
        final_answer_text = f"(원래 정답: {real_ans})"

    script_content = f"""(인트로 BGM 🎵)
성우: "{final_q}"
성우: "3초 안에 맞춰보세요!"

(효과음 ⏰ 3..2..1..)

성우: "정답은 {ans_idx}번! {final_answer_text} 님입니다!"
성우: "맞히셨다면 구독 좋아요!"
"""
    st.markdown(f'<div class="script-box"><pre class="script-text">{script_content}</pre></div>', unsafe_allow_html=True)

else:
    # 초기 안내 화면
    st.info("👈 왼쪽 사이드바에서 색상을 정하고 '🎲 새 퀴즈 뽑기' 버튼을 눌러주세요!")
    st.markdown("<h3 style='text-align: center; color: #888;'>버튼을 누르면 쇼츠 기획안이 나타납니다.</h3>", unsafe_allow_html=True)