import streamlit as st
import random

# --- [기본 설정] ---
st.set_page_config(page_title="트로트 쇼츠 생성기", page_icon="🎤")

# --- [비밀번호 보안] ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    
    # 비밀번호 입력창
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

# --- [메인 기능] ---
st.title("🎤 트로트 4지선다 쇼츠 생성기")
st.markdown("버튼을 누르면 **랜덤 문제 + 대본**이 생성됩니다.")

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("🎲 퀴즈 뽑기 (Click)", type="primary"):
        # 1. 정답 가수 뽑기
        correct_answer = random.choice(TROT_SINGERS)
        
        # 2. 오답 가수 3명 뽑기 (정답 제외)
        wrong_answers = random.sample([s for s in TROT_SINGERS if s != correct_answer], 3)
        
        # 3. 보기 섞기
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        
        # 4. 질문 고르기
        question = random.choice(QUIZ_TEMPLATES).format(name=correct_answer)
        
        # 세션에 저장
        st.session_state['quiz_data'] = {
            "q": question,
            "options": options,
            "answer": correct_answer,
            "ans_idx": options.index(correct_answer) + 1
        }

with col2:
    if 'quiz_data' in st.session_state:
        data = st.session_state['quiz_data']
        
        # 결과 화면
        st.success(f"Q. {data['q']}")
        
        st.info(f"1️⃣ {data['options'][0]}")
        st.info(f"2️⃣ {data['options'][1]}")
        st.info(f"3️⃣ {data['options'][2]}")
        st.info(f"4️⃣ {data['options'][3]}")
        
        st.divider()
        
        st.subheader("📜 쇼츠용 대본")
        script = f"""
(인트로 - 긴장감 있는 음악 🎵)
성우: "{data['q']}"
성우: "3초 안에 찾아보세요!"

(타이머 효과음 째깍째깍... ⏰)
성우: "3! 2! 1!"

(정답 효과음 딩동댕! 🎉)
성우: "정답은... {data['ans_idx']}번! {data['answer']} 님입니다!"
성우: "맞히셨다면 '좋아요' 한 번 부탁드려요!"
"""
        st.code(script, language="text")
        st.warning(f"💡 [편집 팁] 구글에서 '{data['options'][0]}', '{data['options'][1]}'... 사진을 순서대로 찾아 배치하세요!")