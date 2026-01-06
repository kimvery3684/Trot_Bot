import streamlit as st
import random
import urllib.parse # 한글을 URL로 바꾸기 위해 필요

# --- [기본 설정] ---
st.set_page_config(page_title="트로트 쇼츠 생성기 (Pro)", page_icon="🎤", layout="wide")

# --- [비밀번호 보안] ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    
    st.text_input("비밀번호를 입력하세요", type="password", key="password_input", on_change=password_entered)
    return False

def password_entered():
    if st.session_state["password_input"] == st.secrets["APP_PASSWORD"]:
        st.session_state.password_correct = True
        del st.session_state["password_input"]
    else:
        st.error("비밀번호가 틀렸습니다.")

if not check_password():
    st.stop()

# --- [데이터: 가수 100명 리스트] ---
TROT_SINGERS = [
    "임영웅", "영탁", "이찬원", "김호중", "정동원", "장민호", "김희재", "나훈아", "남진", "송가인",
    "장윤정", "홍진영", "박군", "박서진", "진성", "설운도", "태진아", "송대관", "김연자", "주현미",
    "양지은", "전유진", "안성훈", "박지현", "손태진", "에녹", "신성", "민수현", "김다현", "김태연",
    "요요미", "마이진", "린", "박구윤", "신유", "금잔디", "조항조", "강진", "김수희", "하춘화",
    "현숙", "문희옥", "김혜연", "진해성", "홍지윤", "황영웅", "공훈", "김중연", "박민수", "나상도",
    "최수호", "진욱", "박성온", "정서주", "배아현", "오유진", "미스김", "나영", "김소연", "정슬",
    "박주희", "김수찬", "나태주", "강혜연", "윤수현", "조정민", "설하윤", "류지광", "김경민", "남승민",
    "황윤성", "강태관", "김나희", "정미애", "홍자", "정다경", "은가은", "별사랑", "김의영", "황민호",
    "황민우", "이대원", "신인선", "노지훈", "양지원", "한강", "재하", "신승태", "최우진", "성리",
    "추혁진", "박상철", "서주경", "한혜진", "유지나", "김용필", "조명섭"
]

# --- [데이터: 질문 템플릿] ---
QUIZ_TEMPLATES = [
    "다음 중 '{name}' 님은 누구일까요?",
    "이 멋진 무대의 주인공, '{name}'을(를) 찾아보세요!",
    "눈만 봐도 아시겠죠? '{name}' 님은 몇 번?",
    "천상의 목소리! '{name}' 님을 찾아주세요.",
    "트로트계의 아이돌! '{name}' 님은 어디에?",
    "국민 가수 '{name}' 님의 사진을 고르세요."
]

# --- [함수: 임시 이미지 URL 생성] ---
def get_placeholder_image(text, color="795548"):
    # 한글이 깨지지 않게 인코딩
    encoded_text = urllib.parse.quote(text)
    # via.placeholder.com 서비스를 이용해 임시 이미지 생성
    return f"https://via.placeholder.com/400x400/{color}/ffffff.png?text={encoded_text}"

# --- [메인 기능] ---
st.title("🎤 트로트 쇼츠 생성기 (Pro Ver.)")
st.markdown("랜덤 생성 후, **텍스트를 직접 수정**할 수 있습니다. 사진 자리를 확인하세요!")

# 화면 레이아웃: 왼쪽(버튼) vs 오른쪽(결과창)
col_control, col_result = st.columns([1, 3])

# === [왼쪽 컨트롤 패널] ===
with col_control:
    st.subheader("⚙️ 컨트롤")
    if st.button("🎲 랜덤 퀴즈 새로 뽑기 (Click)", type="primary", use_container_width=True):
        # 1. 랜덤 데이터 생성
        correct_answer = random.choice(TROT_SINGERS)
        wrong_answers = random.sample([s for s in TROT_SINGERS if s != correct_answer], 3)
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        question_initial = random.choice(QUIZ_TEMPLATES).format(name=correct_answer)
        
        # 2. 세션 상태 초기화 (새로 뽑을 때마다 입력창 리셋용)
        st.session_state['generated'] = True
        st.session_state['q_draft'] = question_initial
        st.session_state['opt1_draft'] = options[0]
        st.session_state['opt2_draft'] = options[1]
        st.session_state['opt3_draft'] = options[2]
        st.session_state['opt4_draft'] = options[3]
        st.session_state['answer_real'] = correct_answer # 실제 정답은 숨겨둠

    st.divider()
    st.info("💡 **사용팁**\n\n1. 버튼을 눌러 초안을 만듭니다.\n2. 오른쪽에서 멘트와 이름을 수정합니다.\n3. 수정된 내용이 아래 대본에 반영됩니다.")

# === [오른쪽 결과 패널] ===
with col_result:
    if st.session_state.get('generated'):
        # 1. 질문 편집 영역
        st.subheader("📺 화면 구성 및 텍스트 편집")
        final_q = st.text_input("🔻 질문 멘트 (수정 가능)", value=st.session_state['q_draft'], key="q_edit")

        st.markdown("---")

        # 2. 4분할 사진 레이아웃 (이미지 + 편집 가능한 텍스트)
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)

        # 보기 1번
        with c1:
            opt1_val = st.text_input("1번 보기 이름 (수정 가능)", value=st.session_state['opt1_draft'], key="opt1_edit")
            st.image(get_placeholder_image(f"1. {opt1_val}", "E91E63"), use_container_width=True, caption="여기에 이분 사진을 넣으세요")
        # 보기 2번
        with c2:
            opt2_val = st.text_input("2번 보기 이름 (수정 가능)", value=st.session_state['opt2_draft'], key="opt2_edit")
            st.image(get_placeholder_image(f"2. {opt2_val}", "9C27B0"), use_container_width=True, caption="여기에 이분 사진을 넣으세요")
        # 보기 3번
        with c3:
            opt3_val = st.text_input("3번 보기 이름 (수정 가능)", value=st.session_state['opt3_draft'], key="opt3_edit")
            st.image(get_placeholder_image(f"3. {opt3_val}", "673AB7"), use_container_width=True, caption="여기에 이분 사진을 넣으세요")
        # 보기 4번
        with c4:
            opt4_val = st.text_input("4번 보기 이름 (수정 가능)", value=st.session_state['opt4_draft'], key="opt4_edit")
            st.image(get_placeholder_image(f"4. {opt4_val}", "3F51B5"), use_container_width=True, caption="여기에 이분 사진을 넣으세요")

        st.divider()

        # 3. 최종 대본 생성 (수정된 내용 반영)
        st.subheader("📜 최종 성우 대본 (자동 업데이트됨)")
        
        # 현재 입력된 보기들 중에서 진짜 정답 찾기
        current_options = [opt1_val, opt2_val, opt3_val, opt4_val]
        real_ans = st.session_state['answer_real']
        
        try:
            # 수정 과정에서 정답 이름을 바꿔버렸을 경우를 대비한 안전장치
            ans_idx = current_options.index(real_ans) + 1
            final_answer_text = real_ans
        except ValueError:
             # 만약 사용자가 정답 이름을 엉뚱하게 바꿨다면?
            ans_idx = "?"
            final_answer_text = f"(원래 정답은 '{real_ans}'였습니다. 이름을 너무 많이 바꾸셨네요!)"

        script = f"""
(인트로 - 긴장감 넘치는 BGM 🎵)
성우: "{final_q}"
성우: "자, 3초 드립니다! 눈 크게 뜨세요!"

(타이머 효과음 째깍째깍... ⏰)
화면 자막: 3... 2... 1...

(정답 공개 효과음 빠밤! 🎉)
성우: "정답은... 바로 {ans_idx}번!"
성우: "{final_answer_text} 님입니다! 모두 맞히셨나요?"
(아웃트로 - 구독 좋아요 멘트)
"""
        st.text_area("대본 복사하기", script, height=250)

    else:
        # 아직 버튼 안 눌렀을 때
        st.info("👈 왼쪽의 '🎲 랜덤 퀴즈 새로 뽑기' 버튼을 눌러주세요!")