# pages/chat.py

# ==============================
# 필요한 라이브러리 불러오기
# ==============================
import streamlit as st
from openai import OpenAI

# ==============================
# 페이지 설정
# ==============================
st.set_page_config(
    page_title="AI 채팅",
    page_icon="🤖"
)

st.title("🤖 AI 채팅")
st.caption("질문을 입력하면 AI가 답변해요.")

# ==============================
# Gemini API 키 불러오기
# (Streamlit Secrets 사용)
# ==============================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("API 키가 설정되지 않았어요.")
    st.stop()

# ==============================
# OpenAI 방식으로 Gemini 연결
# ==============================
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# ==============================
# AI 성격 설정
# (화면에는 표시되지 않음)
# ==============================
SYSTEM_PROMPT = """
너는 중고등학생에게 설명하는 친절한 정보 선생님이야.
어려운 말은 쉬운 말로 바꿔 주고,
반드시 순수 한국어로만 답해.
"""

# ==============================
# 대화 저장 공간 만들기
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# 이전 대화 화면에 표시
# ==============================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==============================
# 사용자 입력창
# ==============================
user_input = st.chat_input("질문을 입력하세요")

if user_input:

    # 사용자 말 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # 사용자 말풍선 표시
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 말풍선
    with st.chat_message("assistant"):

        # 글자가 실시간으로 나올 공간
        answer_box = st.empty()

        try:
            # 시스템 프롬프트 + 이전 대화 합치기
            send_messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            send_messages.extend(st.session_state.messages)

            # 스트리밍 요청
            stream = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=send_messages,
                stream=True
            )

            full_text = ""

            # 글자가 조금씩 나오게 만들기
            for chunk in stream:

                try:
                    text = chunk.choices[0].delta.content

                    if text:
                        full_text += text
                        answer_box.markdown(full_text)

                except:
                    pass

            # 대화 기억 저장
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_text
                }
            )

        except:
            # 오류 발생 시 친절한 문구만 표시
            answer_box.markdown(
                "죄송해요. 지금은 답변을 가져오지 못했어요. 잠시 후 다시 시도해 주세요."
            )
