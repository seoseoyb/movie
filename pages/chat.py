import streamlit as st
from openai import OpenAI

# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="냥냥 고양이 추천소",
    page_icon="🐱",
    layout="wide"
)


# ==========================================
# 고양이 정보
# ==========================================

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
        "feature": "차분하고 사람과 함께 있는 것을 좋아하는 편"
    },
    "메인쿤": {
        "emoji": "💛",
        "feature": "큰 체격과 온순한 성격으로 알려진 편"
    },
    "샴": {
        "emoji": "💙",
        "feature": "사람과의 상호작용을 좋아하고 활발한 편"
    },
    "브리티시 숏헤어": {
        "emoji": "🤍",
        "feature": "차분하고 비교적 독립적인 편"
    },
    "페르시안": {
        "emoji": "🩷",
        "feature": "조용하고 느긋한 분위기를 선호하는 편"
    },
    "러시안 블루": {
        "emoji": "💜",
        "feature": "조용하고 신중하며 보호자와 친밀해지는 편"
    },
}


# ==========================================
# 화면 디자인
# ==========================================

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


/* ==========================================
   날아다니는 고양이
   ========================================== */

.cat {
    position: fixed;
    left: -100px;
    z-index: 0;
    pointer-events: none;
    opacity: 0.7;
}

.cat1 {
    top: 12%;
    font-size: 45px;
    animation: fly1 14s linear infinite;
}

.cat2 {
    top: 32%;
    font-size: 35px;
    animation: fly2 18s linear infinite;
    animation-delay: 3s;
}

.cat3 {
    top: 57%;
    font-size: 50px;
    animation: fly3 16s linear infinite;
    animation-delay: 6s;
}

.cat4 {
    top: 78%;
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


/* ==========================================
   제목
   ========================================== */

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


/* ==========================================
   선택 영역
   ========================================== */

.choice-title {
    font-family:
        "Arial Rounded MT Bold",
        "Trebuchet MS",
        "Malgun Gothic",
        sans-serif;

    font-size: 25px;
    font-weight: 800;

    color: #604b73;

    margin-top: 20px;
    margin-bottom: 10px;
}


/* ==========================================
   채팅창
   ========================================== */

[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.90);

    border-radius: 22px;

    padding: 10px;

    margin-bottom: 12px;

    box-shadow:
        0 6px 20px rgba(100, 80, 120, 0.08);
}

[data-testid="stChatInput"] {
    border-radius: 20px;
}


/* 앱 내용 */
[data-testid="stAppViewContainer"] {
    background: transparent;
    position: relative;
    z-index: 1;
}

header {
    background: transparent !important;
}


/* 추천 카드 */
.recommend-card {
    background: rgba(255, 255, 255, 0.9);

    border-radius: 20px;

    padding: 15px;

    margin-top: 10px;

    box-shadow:
        0 5px 18px rgba(100, 80, 120, 0.08);
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
    '내 성격과 원하는 고양이를 골라보면 '
    '나에게 어울리는 고양이를 찾아줄게냥'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# Gemini 연결
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
너는 '냥냥 고양이 추천소'라는 고양이 품종 추천 챗봇이다.

사용자가 처음 선택한 성격과 원하는 고양이 특징을 바탕으로
고양이 품종을 바로 추천한다.

그 이후 사용자가 추가 조건이나 취향을 말하면
기존 조건을 유지하면서 새 조건을 추가해 후보를 좁히거나
필요하다면 새로운 품종을 추천한다.

중요한 규칙:

1. 사용자가 충분한 정보를 선택했다면 추가 질문부터 하지 말고 바로 추천한다.
2. 사용자가 처음 선택한 조건을 기억한다.
3. 이후 대화에서 사용자가 새로운 조건을 말하면 기존 조건과 합쳐서 판단한다.
4. 조건이 추가되면서 기존 추천이 맞지 않게 되면 새로운 후보를 제시한다.
5. 고양이 품종의 성격은 개체마다 다를 수 있으므로 절대적으로 단정하지 않는다.
6. 품종의 일반적인 경향을 설명한다.
7. 추천할 때 왜 조건에 맞는지 설명한다.
8. 장점뿐 아니라 고려할 점도 알려준다.
9. 사용자가 원하는 경우 후보를 1~3개 정도로 좁혀준다.
10. 한국어로 대답한다.
11. 친근하고 귀엽게 대답한다.
12. 답변의 마지막 글자는 반드시 '냥'으로 끝낸다.

처음 추천할 때 형식:

🐱 가장 잘 어울리는 고양이
품종: ○○

💗 왜 잘 맞을까?
사용자가 선택한 조건과 연결해서 설명

✨ 특징
고양이의 대표적인 특징

⚠️ 알아둘 점
키울 때 고려할 점

🐾 다른 후보
필요한 경우 다른 품종 1~2개

추가 조건이 들어오면:

🐾 조건을 반영해서 다시 골라봤어!

이전 조건 + 새로운 조건을 반영하여
후보를 좁히거나 새롭게 추천한다.
"""


# ==========================================
# 대화 기록
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# 초기 선택 화면
# ==========================================

if len(st.session_state.messages) == 0:

    st.markdown(
        '<div class="choice-title">🐾 나는 이런 성격이야</div>',
        unsafe_allow_html=True
    )

    personality_options = [
        "🏠 조용하고 차분한 편",
        "🎉 활발하고 노는 걸 좋아해",
        "💕 애교 많고 정이 많은 편",
        "🧘 혼자 있는 시간도 좋아해",
        "👀 새로운 걸 좋아하고 호기심이 많아",
        "😌 느긋하고 여유로운 편",
    ]

    personality = st.multiselect(
        "나를 가장 잘 나타내는 것을 골라줘!",
        personality_options,
        placeholder="여러 개 골라도 돼냥!"
    )


    st.markdown(
        '<div class="choice-title">🐱 이런 고양이를 찾고 있어</div>',
        unsafe_allow_html=True
    )

    cat_options = [
        "💕 사람을 잘 따르는 고양이",
        "⚡ 활발하고 장난기 많은 고양이",
        "🌙 차분하고 조용한 고양이",
        "🥰 애교가 많은 고양이",
        "🐾 독립적인 고양이",
        "✨ 털이 복슬복슬한 고양이",
        "🧹 털 관리가 비교적 쉬운 고양이",
        "🏡 집에서 편안하게 지내는 고양이",
        "🗣️ 사람과 상호작용을 좋아하는 고양이",
    ]

    cat_style = st.multiselect(
        "원하는 특징을 골라줘!",
        cat_options,
        placeholder="여러 개 골라도 돼냥!"
    )


    # 추천 버튼
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

            # 선택한 내용을 하나의 문장으로 만들기
            selected_text = f"""
내 성격:
{", ".join(personality)}

내가 원하는 고양이:
{", ".join(cat_style)}
"""

            # 사용자 메시지로 저장
            st.session_state.messages.append({
                "role": "user",
                "content": selected_text
            })

            # AI에게 보내기
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

                with st.spinner("나에게 어울리는 고양이를 찾는 중이냥..."):

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

        # AI 답변에서 품종 찾기
        if message["role"] == "assistant":

            found = []

            for breed in CAT_IMAGES:

                if breed in message["content"]:
                    if breed not in found:
                        found.append(breed)

            found = found[:3]

            if found:

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

                        st.write(
                            info["feature"]
                        )


# ==========================================
# 추가 대화
# ==========================================

if st.session_state.messages:

    user_input = st.chat_input(
        "더 원하는 조건을 말해줘! 예: 털이 적게 빠졌으면 좋겠어 🐱"
    )

    if user_input:

        # 사용자 메시지 저장
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        if client is None:

            st.session_state.messages.append({
                "role": "assistant",
                "content":
                "잠시 문제가 생겼어요. 설정을 확인해 주세요냥"
            })

            st.rerun()

        else:

            api_messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            # 지금까지의 모든 대화 전달
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

                                placeholder.markdown(
                                    answer
                                )

                    answer = answer.rstrip()

                    if answer and not answer.endswith("냥"):
                        answer += "냥"

                    placeholder.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.rerun()

            except Exception:

                st.session_state.messages.append({
                    "role": "assistant",
                    "content":
                    "잠시 문제가 생겼어요. 조금 후에 다시 시도해 주세요냥"
                })

                st.rerun()
