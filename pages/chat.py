import streamlit as st
from openai import OpenAI

# -----------------------------
# 페이지 기본 설정
# -----------------------------
st.set_page_config(
    page_title="냥냥 고양이 추천소",
    page_icon="🐱",
    layout="wide"
)


# -----------------------------
# 고양이 정보
# -----------------------------
CAT_IMAGES = {
    "랙돌": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Ragdoll%20cat.jpg",
    "메인쿤": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Maine_Coon_cat.jpg",
    "샴": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Siamese_cat.jpg",
    "브리티시 숏헤어": "https://commons.wikimedia.org/wiki/Special:Redirect/file/British_Shorthair.jpg",
    "페르시안": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Persian_cat.jpg",
    "러시안 블루": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Russian_Blue.jpg",
}

CAT_INFO = {
    "랙돌": {
        "emoji": "🩵",
        "feature": "차분하고 사람과 함께 있는 것을 좋아하는 편",
    },
    "메인쿤": {
        "emoji": "💛",
        "feature": "큰 체격과 온순한 성격으로 유명한 편",
    },
    "샴": {
        "emoji": "💙",
        "feature": "사람과 상호작용하는 것을 좋아하고 활발한 편",
    },
    "브리티시 숏헤어": {
        "emoji": "🤍",
        "feature": "독립적이면서도 차분하고 안정적인 편",
    },
    "페르시안": {
        "emoji": "🩷",
        "feature": "조용하고 느긋한 분위기를 선호하는 편",
    },
    "러시안 블루": {
        "emoji": "💜",
        "feature": "조용하고 신중하며 보호자와 친밀해지는 편",
    },
}


# -----------------------------
# 화면 디자인
# -----------------------------
st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background: linear-gradient(
        135deg,
        #fff7fb 0%,
        #f7f1ff 50%,
        #fffaf1 100%
    );
}

/* -----------------------------
   날아다니는 고양이
   ----------------------------- */

.cat {
    position: fixed;
    left: -100px;
    z-index: 0;
    pointer-events: none;
    opacity: 0.75;
}

/* 첫 번째 고양이 */
.cat1 {
    top: 12%;
    font-size: 45px;
    animation: fly1 14s linear infinite;
}

/* 두 번째 고양이 */
.cat2 {
    top: 30%;
    font-size: 35px;
    animation: fly2 18s linear infinite;
    animation-delay: 3s;
}

/* 세 번째 고양이 */
.cat3 {
    top: 55%;
    font-size: 50px;
    animation: fly3 16s linear infinite;
    animation-delay: 6s;
}

/* 네 번째 고양이 */
.cat4 {
    top: 75%;
    font-size: 32px;
    animation: fly4 20s linear infinite;
    animation-delay: 1s;
}


/* 고양이가 화면을 가로질러 이동 */
@keyframes fly1 {
    0% {
        transform: translateX(0) translateY(0) rotate(-10deg);
    }

    50% {
        transform: translateX(55vw) translateY(-40px) rotate(10deg);
    }

    100% {
        transform: translateX(110vw) translateY(20px) rotate(-5deg);
    }
}

@keyframes fly2 {
    0% {
        transform: translateX(0) translateY(20px) rotate(5deg);
    }

    50% {
        transform: translateX(50vw) translateY(-50px) rotate(-8deg);
    }

    100% {
        transform: translateX(110vw) translateY(10px) rotate(8deg);
    }
}

@keyframes fly3 {
    0% {
        transform: translateX(0) translateY(0) rotate(8deg);
    }

    50% {
        transform: translateX(60vw) translateY(-60px) rotate(-8deg);
    }

    100% {
        transform: translateX(110vw) translateY(20px) rotate(5deg);
    }
}

@keyframes fly4 {
    0% {
        transform: translateX(0) translateY(-20px);
    }

    50% {
        transform: translateX(55vw) translateY(40px);
    }

    100% {
        transform: translateX(110vw) translateY(-10px);
    }
}


/* -----------------------------
   큰 동글동글한 제목
   ----------------------------- */

.main-title {
    text-align: center;

    font-family:
        "Arial Rounded MT Bold",
        "Trebuchet MS",
        "Malgun Gothic",
        sans-serif;

    font-size: 56px;
    font-weight: 900;

    letter-spacing: -3px;

    color: #604b73;

    margin-top: 15px;
    margin-bottom: 8px;
}


/* 제목 아래 설명 */
.main-subtitle {
    text-align: center;

    font-family:
        "Malgun Gothic",
        sans-serif;

    font-size: 18px;
    font-weight: 500;

    color: #887593;

    margin-bottom: 32px;
}


/* -----------------------------
   채팅 메시지
   ----------------------------- */

[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.90);

    border-radius: 22px;

    padding: 10px;

    margin-bottom: 12px;

    box-shadow:
        0 6px 20px rgba(100, 80, 120, 0.08);
}


/* -----------------------------
   입력창
   ----------------------------- */

[data-testid="stChatInput"] {
    border-radius: 20px;
}


/* Streamlit 기본 배경 투명하게 */
[data-testid="stAppViewContainer"] {
    background: transparent;
    position: relative;
    z-index: 1;
}


/* 상단 헤더 투명 */
header {
    background: transparent !important;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# 날아다니는 고양이
# -----------------------------
st.markdown("""
<div class="cat cat1">🐈</div>
<div class="cat cat2">🐱</div>
<div class="cat cat3">🐈‍⬛</div>
<div class="cat cat4">😺</div>
""", unsafe_allow_html=True)


# -----------------------------
# 큰 제목
# -----------------------------
st.markdown(
    '<div class="main-title">🐱 냥냥 고양이 추천소 🐱</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    '나의 성격과 원하는 고양이 스타일을 알려주면 '
    '나에게 어울리는 고양이를 찾아줄게냥'
    '</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Gemini 연결
# -----------------------------
try:
    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
except Exception:
    client = None


# -----------------------------
# AI의 역할
# -----------------------------
SYSTEM_PROMPT = """
너는 '냥냥 고양이 추천소'라는 고양이 품종 추천 챗봇이다.

사용자가 자신의 성격, 생활 방식, 원하는 고양이의 외모나 성격,
활동량, 털 관리 정도, 사람과의 친밀도 등을 이야기하면
그 조건을 바탕으로 어울리는 고양이 품종을 추천한다.

중요한 규칙:

1. 한 품종의 모든 고양이가 같은 성격이라고 단정하지 않는다.
2. 품종의 일반적인 경향과 개체 차이가 있을 수 있음을 자연스럽게 설명한다.
3. 충분한 정보가 없다면 필요한 질문을 먼저 한다.
4. 정보가 충분하다면 1~3개의 품종을 추천한다.
5. 각 추천에는 왜 잘 맞는지 설명한다.
6. 장점뿐 아니라 함께 고려해야 할 점도 알려준다.
7. 한국어로만 대답한다.
8. 친근하고 귀엽지만 지나치게 유치하지 않게 말한다.
9. 모든 답변의 마지막 글자는 반드시 '냥'으로 끝낸다.
10. 문장 중간에는 불필요하게 '냥'을 붙이지 않는다.

추천 결과를 보여줄 때는 가능하면 다음 형식을 사용한다.

🐱 가장 잘 어울리는 고양이
품종: ○○

💗 왜 잘 맞을까?
...

✨ 특징
...

⚠️ 알아둘 점
...

🐾 다른 후보
...
"""


# -----------------------------
# 대화 기록 저장
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:

    st.markdown("### 🐾 냥냥 추천소")

    st.write(
        "나의 성격이나 원하는 고양이 스타일을 "
        "편하게 이야기해보세요!"
    )

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.markdown("### 💡 이렇게 말해보세요")

    st.write("🐱 조용하고 얌전한 고양이를 좋아해")
    st.write("🏠 집에 있는 시간이 별로 없어")
    st.write("💕 사람을 좋아하는 고양이가 좋아")
    st.write("✨ 털이 짧은 고양이를 원해")


# -----------------------------
# 이전 대화 보여주기
# -----------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------
# 고양이 추천 카드
# -----------------------------
def show_cat_cards(text):

    found = []

    for breed in CAT_IMAGES:

        if breed in text and breed not in found:
            found.append(breed)

    # 최대 3개까지만 표시
    found = found[:3]

    if not found:
        return

    st.markdown("### 🐾 추천 고양이")

    columns = st.columns(len(found))

    for column, breed in zip(columns, found):

        with column:

            st.image(
                CAT_IMAGES[breed],
                use_container_width=True
            )

            info = CAT_INFO[breed]

            st.markdown(
                f"### {info['emoji']} {breed}"
            )

            st.write(info["feature"])


# -----------------------------
# 사용자 입력
# -----------------------------
user_input = st.chat_input(
    "어떤 고양이를 찾고 있냥? 🐱"
)


# -----------------------------
# 챗봇 실행
# -----------------------------
if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 답변
    with st.chat_message("assistant"):

        if client is None:

            answer = "잠시 문제가 생겼어요. 설정을 확인해 주세요냥"
            st.markdown(answer)

        else:

            # API에 보낼 메시지
            api_messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            # 이전 대화도 함께 전달
            api_messages.extend(
                st.session_state.messages
            )

            try:

                response = client.chat.completions.create(
                    model="gemini-3.5-flash-lite",
                    messages=api_messages,
                    stream=True
                )

                # 실시간으로 답변 표시
                answer = ""

                message_placeholder = st.empty()

                for chunk in response:

                    if chunk.choices:

                        delta = chunk.choices[0].delta.content

                        if delta:
                            answer += delta
                            message_placeholder.markdown(answer)

                # 마지막에 '냥'이 없으면 붙이기
                answer = answer.rstrip()

                if answer and not answer.endswith("냥"):
                    answer += "냥"

                message_placeholder.markdown(answer)

                # 대화 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                # 추천 고양이 카드
                show_cat_cards(answer)

            except Exception:

                error_message = (
                    "잠시 문제가 생겼어요. "
                    "조금 후에 다시 시도해 주세요냥"
                )

                st.markdown(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
