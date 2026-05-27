import streamlit as st
import google.generativeai as genai

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💌",
    layout="centered"
)

st.title("💌 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반 상담 챗봇")

# -----------------------------
# API KEY 불러오기
# -----------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("❌ secrets.toml에서 GEMINI_API_KEY를 찾을 수 없습니다.")
    st.stop()

# Gemini 설정
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"❌ Gemini API 설정 오류: {e}")
    st.stop()

# -----------------------------
# 모델 생성
# -----------------------------
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction="""
        너는 공감 능력이 뛰어난 연애 상담 챗봇이다.
        
        사용자의 감정을 존중하며 부드럽고 친절하게 답변한다.
        필요한 경우 현실적인 조언도 제공한다.
        연애 외 주제도 자연스럽게 대화 가능하다.
        """
    )
except Exception as e:
    st.error(f"❌ 모델 생성 오류: {e}")
    st.stop()

# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    try:
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"❌ 채팅 세션 생성 오류: {e}")
        st.stop()

# -----------------------------
# 이전 대화 출력
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# 사용자 입력
# -----------------------------
user_input = st.chat_input("연애 고민을 이야기해보세요...")

if user_input:
    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    # 챗봇 응답
    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            try:
                response = st.session_state.chat_session.send_message(
                    user_input
                )

                bot_reply = response.text

                st.markdown(bot_reply)

                # 응답 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_reply
                })

            except Exception as e:
                error_message = f"""
                ❌ 오류가 발생했습니다.

                잠시 후 다시 시도해주세요.

                오류 내용:
                {e}
                """

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "오류가 발생했어요 😢"
                })

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.header("⚙️ 설정")

    if st.button("대화 초기화"):
        st.session_state.messages = []

        try:
            st.session_state.chat_session = model.start_chat(history=[])
            st.success("대화가 초기화되었습니다.")
        except Exception as e:
            st.error(f"초기화 오류: {e}")

    st.divider()

    st.markdown("""
    ### 💡 사용 예시
    - 썸 상대가 연락이 줄었어요
    - 고백 타이밍이 고민돼요
    - 헤어진 후 너무 힘들어요
    - 그냥 오늘 우울해요
    """)
