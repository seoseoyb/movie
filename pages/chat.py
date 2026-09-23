import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="냥냥 고양이 추천소",
    page_icon="🐱",
    layout="wide"
)

# ==========================================
# 고양이 사진
# ==========================================

CAT_IMAGES = {
    "랙돌": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Ragdoll%20cat.jpg",
    "메인쿤": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Maine_Coon_cat.jpg",
    "샴": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Siamese_cat.jpg",
    "브리티시 숏헤어": "https://commons.wikimedia.org/wiki/Special:Redirect/file/British_Shorthair.jpg",
    "페르시안": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Persian_cat.jpg",
    "러시안 블루": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Russian_Blue.jpg"
}

CAT_INFO = {
    "랙돌": "차분하고 사람과 함께 있는 것을 좋아하는 편",
    "메인쿤": "큰 체격과 온순한 성격으로 알려진 편",
    "샴": "사람과의 상호작용을 좋아하고 활발한 편",
    "브리티시 숏헤어": "차분하고 비교적 독립적인 편",
    "페르시안": "조용하고 느긋한 분위기를 선호하는 편",
    "러시안 블루": "조용하고 신중하며 보호자와 친밀해지는 편"
}

# ==========================================
# 화면 디자인
# ==========================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fff7fb 0%,
        #f5f0ff 50%,
        #fffaf0 100%
    );
}

/* 날아다니는 고양이 */
.cat {
    position: fixed;
    left: -100px;
    z-index: 0;
    pointer-events: none;
    opacity: 0.75;
}

.cat1 {
    top: 12%;
    font-size: 45px;
    animation: fly1 14s linear infinite;
}

.cat2 {
    top: 30%;
    font-size: 35px;
    animation: fly2 18s linear infinite;
    animation-delay: 3s;
}

.cat3 {
    top: 55%;
    font-size: 50px;
    animation: fly3 16s linear infinite;
    animation-delay: 6s;
}

.cat4 {
    top: 75%;
    font-size: 32px;
    animation: fly4 20s linear infinite;
    animation-delay: 1s;
}

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

/* 큰 동글동글한 제목 */
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

.main-subtitle {
    text-align: center;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 18px;
    font-weight: 500;
    color: #887593;
    margin-bottom: 30px;
}

/* 선택 영역 */
.choice-title {
    font-family:
        "Arial Rounded MT Bold",
        "Trebuchet MS",
        "Malgun Gothic",
        sans-serif;
    font-size: 25px;
    font-weight: 900;
    color: #604b73;
    margin-top: 15px;
    margin-bottom: 8px;
}

/* 채팅 카드 */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.90);
    border-radius: 22px;
    padding: 10px;
    margin-bottom: 12px;
    box-shadow: 0 6px 20px rgba(100, 80, 120, 0.08);
}

/* 입력창 */
[data-testid="stChatInput"] {
    border-radius: 20px;
}

/* 전체 내용 */
[data-testid="stAppViewContainer"] {
    background: transparent;
    position: relative;
    z-index: 1;
}

header {
    background: transparent !important;
}

/* 추천 제목 */
.recommend-title {
    font-family:
        "Arial Rounded MT Bold",
        "Trebuchet MS",
        "Malgun Gothic",
        sans-serif;
    font-size: 27px;
    font-weight: 900;
    color: #604b73;
    margin-top: 20px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 날아다니는 고양이
# ==========================================

st.markdown("""
<div class="cat cat1">🐈</div>
<div class="cat cat2">🐱</div>
<div class="cat cat3">🐈‍⬛</div>
<div class="cat cat4">😺</div>
""", unsafe_allow_html=True)

# ==========================================
# 제목
# ==========================================

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

# ==========================================
# Gemini
# ==========================================

try:
    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
except Exception:
    client = None

# ==========================================
# AI 역할
# ==========================================

SYSTEM_PROMPT = """
너는 '냥냥 고양이 추천소'라는 고양이 품종 추천 AI다.

사용자가 처음 선택한 성격과 원하는 고양이 특징을 바탕으로
추가 질문을 하지 말고 바로 고양이를 추천한다.

처음 추천 이후에는 사용자가 새로운 조건을 말할 수 있다.
새로운 조건이 들어오면 이전 조건을 기억하고 새 조건까지 합쳐서
추천 후보를 좁히거나 새로운 품종을 추천한다.

예:
사용자: 털이 많이 빠지는 건 싫어
→ 기존 조건 + 털 관리 조건을 반영해서 다시 추천

사용자: 좀 더 애교가 많았으면 좋겠어
→ 기존 조건 + 애교 조건을 반영해서 후보를 좁힘

사용자: 아파트에서 키울 거야
→ 기존 조건 + 생활환경까지 고려

품종의 성격을 절대적으로 단정하지 않는다.
같은 품종이어도 개체마다 성격이 다를 수 있음을 알려준다.

추천할 때는:
🐱 가장 잘 어울리는 고양이
💗 왜 잘 맞을까?
✨ 특징
⚠️ 알아둘 점
🐾 다른 후보

를 적절히 사용한다.

한국어로만 답한다.
친근하고 귀엽게 말한다.
답변의 마지막 글자는 반드시 '냥'으로 끝낸다.
"""

# ==========================================
# 대화 기록
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 처음 방문했을 때 선택 화면
# ==========================================

if len(st.session_state.messages) == 0:

    st.markdown(
        '<div class="choice-title">🐾 나는 이런 성격이야</div>',
        unsafe_allow_html=True
    )

    personality = st.multiselect(
        "나와 가까운 것을 골라줘!",
        [
            "🏠 조용하고 차분한 편",
            "🎉 활발하고 노는 걸 좋아해",
            "💕 애교 많고 정이 많은 편",
            "🧘 혼자 있는 시간도 좋아해",
            "👀 호기심이 많아",
            "😌 느긋하고 여유로운 편"
        ],
        placeholder="여러 개 골라도 돼냥!"
    )

    st.markdown(
        '<div class="choice-title">🐱 이런 고양이를 찾고 있어</div>',
        unsafe_allow_html=True
    )

    cat_style = st.multiselect(
        "원하는 특징을 골라줘!",
        [
            "💕 사람을 잘 따르는 고양이",
            "🥰 애교가 많은 고양이",
            "⚡ 활발하고 장난기 많은 고양이",
            "🌙 차분하고 조용한 고양이",
            "🐾 독립적인 고양이",
            "✨ 털이 복슬복슬한 고양이",
            "🧹 털 관리가 쉬운 고양이",
            "🏡 집에서 편안하게 지내는 고양이",
            "🗣️ 사람과 상호작용을 좋아하는 고양이"
        ],
        placeholder="여러 개 골라도 돼냥!"
    )

    if st.button(
        "🐱 이 조건으로 고양이 찾아줘냥!",
        use_container_width=True,
        type="primary"
    ):

        if not personality and not cat_style:
            st.warning(
                "성격이나 원하는 고양이 특징을 하나 이상 골라줘냥!"
            )

        elif client is None:
            st.error(
                "잠시 문제가 생겼어요. 설정을 확인해 주세요냥"
            )

        else:

            selected = f"""
[처음 선택한 조건]

사용자의 성격:
{", ".join(personality) if personality else "선택하지 않음"}

원하는 고양이:
{", ".join(cat_style) if cat_style else "선택하지 않음"}
"""

            st.session_state.messages.append({
                "role": "user",
                "content": selected
            })

            api_messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            api_messages.extend(st.session_state.messages)

            try:

                response = client.chat.completions.create(
                    model="gemini-3.5-flash-lite",
                    messages=api_messages,
                    stream=True
                )

                answer = ""

                for chunk in response:

                    if chunk.choices:

                        delta = chunk.choices[0].delta.content

                        if delta:
                            answer += delta

                answer = answer.rstrip()

                if answer and not answer.endswith("냥"):
                    answer += "냥"

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.rerun()

            except Exception:

                st.session_state.messages.append({
                    "role": "assistant",
                    "content":
                    "잠시 문제가 생겼어요. 다시 시도해 주세요냥"
                })

                st.rerun()

# ==========================================
# 기존 대화 표시
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # AI 답변에 나온 고양이 사진 표시
        if message["role"] == "assistant":

            found = []

            for breed in CAT_IMAGES:

                if breed in message["content"]:

                    if breed not in found:
                        found.append(breed)

            found = found[:3]

            if found:

                st.markdown(
                    '<div class="recommend-title">'
                    '🐾 추천 고양이'
                    '</div>',
                    unsafe_allow_html=True
                )

                columns = st.columns(len(found))

                for column, breed in zip(columns, found):

                    with column:

                        st.image(
                            CAT_IMAGES[breed],
                            use_container_width=True
                        )

                        st.markdown(
                            f"### 🐱 {breed}"
                        )

                        st.write(
                            CAT_INFO[breed]
                        )

# ==========================================
# 추가 대화
# ==========================================

if st.session_state.messages:

    user_input = st.chat_input(
        "더 구체적인 조건을 말해줘! 🐱"
    )

    if user_input:

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        if client is None:

            answer = "잠시 문제가 생겼어요. 설정을 확인해 주세요냥"

        else:

            api_messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            api_messages.extend(
                st.session_state.messages
            )

            try:

                response = client.chat.completions.create(
                    model="gemini-3.5-flash-lite",
                    messages=api_messages,
                    stream=True
                )

                answer = ""

                with st.chat_message("assistant"):

                    placeholder = st.empty()

                    for chunk in response:

                        if chunk.choices:

                            delta = chunk.choices[0].delta.content

                            if delta:

                                answer += delta
                                placeholder.markdown(answer)

                    answer = answer.rstrip()

                    if answer and not answer.endswith("냥"):
                        answer += "냥"

                    placeholder.markdown(answer)

            except Exception:

                answer = (
                    "잠시 문제가 생겼어요. "
                    "조금 후에 다시 시도해 주세요냥"
                )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()
