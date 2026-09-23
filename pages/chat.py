import streamlit as st
from openai import OpenAI

# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="냥냥 고양이 추천소",
    page_icon="🐱",
    layout="wide"
)

# =========================================================
# 고양이 사진
# =========================================================
CAT_IMAGES = {
    "랙돌": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Ragdoll%20cat.jpg",
    "메인쿤": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Maine_Coon_cat.jpg",
    "샴": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Siamese_cat.jpg",
    "브리티시 숏헤어": "https://commons.wikimedia.org/wiki/Special:Redirect/file/British_Shorthair.jpg",
    "페르시안": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Persian_cat.jpg",
    "러시안 블루": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Russian_Blue.jpg",
}

CAT_INFO = {
    "랙돌": "차분하고 사람과 함께 있는 것을 좋아하는 편이며, 온순한 성향으로 알려져 있어요.",
    "메인쿤": "큰 체격과 온순한 성향으로 알려져 있으며 사람과의 교류를 좋아하는 편이에요.",
    "샴": "사람과의 상호작용을 좋아하고 활발하며 호기심이 많은 편이에요.",
    "브리티시 숏헤어": "차분하고 비교적 독립적인 편이라 혼자 있는 시간도 잘 보내는 편이에요.",
    "페르시안": "조용하고 느긋한 분위기를 좋아하며 차분한 생활을 선호하는 편이에요.",
    "러시안 블루": "조용하고 신중한 편이며 보호자와 친밀한 관계를 형성하는 것으로 알려져 있어요.",
}

# =========================================================
# CSS 디자인
# =========================================================
st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background: linear-gradient(
        135deg,
        #fff7fb 0%,
        #f5f0ff 50%,
        #fffaf0 100%
    );
}

/* 페이지 여백 */
.block-container {
    padding-top: 25px;
    padding-bottom: 60px;
}

/* =====================================================
   날아다니는 고양이
   ===================================================== */

.flying-cat {
    position: fixed;
    left: -100px;
    z-index: 0;
    pointer-events: none;
    animation: flycat 12s linear infinite;
    opacity: 0.75;
    font-size: 38px;
}

.cat1 {
    top: 12%;
    animation-delay: 0s;
}

.cat2 {
    top: 32%;
    animation-delay: 4s;
    font-size: 30px;
}

.cat3 {
    top: 58%;
    animation-delay: 8s;
    font-size: 45px;
}

.cat4 {
    top: 78%;
    animation-delay: 2s;
    font-size: 28px;
}

@keyframes flycat {
    0% {
        transform: translateX(-100px) rotate(-8deg);
    }

    50% {
        transform: translateX(55vw) translateY(-40px) rotate(8deg);
    }

    100% {
        transform: translateX(110vw) translateY(10px) rotate(-5deg);
    }
}

/* =====================================================
   제목
   ===================================================== */

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
    margin-top: 5px;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: #887593;
    font-size: 18px;
    margin-bottom: 35px;
}

/* =====================================================
   선택 영역
   ===================================================== */

.section-title {
    font-family:
        "Arial Rounded MT Bold",
        "Trebuchet MS",
        "Malgun Gothic",
        sans-serif;

    color: #604b73;
    font-size: 27px;
    font-weight: 900;
    margin-top: 25px;
    margin-bottom: 15px;
}

/* 선택 버튼 */

div.stButton > button {
    width: 100%;
    min-height: 58px;

    border-radius: 18px;
    border: 2px solid #eadcf2;

    background: rgba(255,255,255,0.88);

    color: #66546f;

    font-size: 16px;
    font-weight: 700;

    transition: all 0.2s ease;
}

div.stButton > button:hover {
    border-color: #cba9df;
    background: #f7edfc;
    transform: translateY(-2px);
}

/* 선택된 버튼 */

.selected-button button {
    background: #ead8f5 !important;
    border-color: #b98bd2 !important;
    color: #604b73 !important;
}

/* 추천 버튼 */

.recommend-button button {
    min-height: 65px !important;
    margin-top: 20px;

    background: #dcb9ee !important;
    border: none !important;

    color: #5a4168 !important;

    font-size: 19px !important;
    font-weight: 900 !important;
}

/* =====================================================
   결과 카드
   ===================================================== */

.result-card {
    background: rgba(255,255,255,0.9);
    border-radius: 28px;
    padding: 22px;
    margin-top: 20px;

    box-shadow:
        0 8px 25px rgba(95,70,110,0.10);
}

.result-name {
    font-family:
        "Arial Rounded MT Bold",
        "Trebuchet MS",
        "Malgun Gothic",
        sans-serif;

    font-size: 29px;
    font-weight: 900;
    color: #604b73;

    margin-bottom: 8px;
}

.result-description {
    color: #75677d;
    font-size: 16px;
    line-height: 1.7;

    margin-bottom: 15px;
}

/* 사진 */
.result-card img {
    border-radius: 20px;
}

/* =====================================================
   채팅
   ===================================================== */

.chat-card {
    background: rgba(255,255,255,0.84);
    border-radius: 22px;

    padding: 18px 22px;
    margin: 12px 0;

    box-shadow:
        0 5px 18px rgba(90,70,100,0.07);
}

.user-card {
    border-left: 5px solid #c9a7e8;
}

.ai-card {
    border-left: 5px solid #f0b6d5;
}

</style>

<div class="flying-cat cat1">🐱</div>
<div class="flying-cat cat2">🐈</div>
<div class="flying-cat cat3">😺</div>
<div class="flying-cat cat4">🐾</div>
""", unsafe_allow_html=True)


# =========================================================
# 제목
# =========================================================
st.markdown(
    '<div class="main-title">🐱 냥냥 고양이 추천소 🐱</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">내 성격과 원하는 고양이를 골라주면 딱 맞는 냥이를 찾아줄게냥!</div>',
    unsafe_allow_html=True
)


# =========================================================
# Gemini 연결
# =========================================================
client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MODEL_NAME = "gemini-3.5-flash-lite"


# =========================================================
# AI 시스템 프롬프트
# =========================================================
SYSTEM_PROMPT = """
너는 '냥냥 고양이 추천소'라는 고양이 품종 추천 AI다.

사용자가 선택한 자신의 성격과 원하는 고양이 특징을 바탕으로
고양이 품종을 추천한다.

처음에는 추가 질문을 하지 말고 바로 추천한다.

추천할 때는 사용자의 조건을 종합해서 가장 잘 맞는 품종을
약 3마리 정도 추천한다.

각 품종마다 반드시 다음 정보를 포함한다.

🐱 품종 이름
💗 왜 사용자에게 잘 맞는지
✨ 주요 특징
⚠️ 알아둘 점

품종의 성격을 절대적으로 단정하지 않는다.
같은 품종이어도 고양이 개체마다 성격이 다를 수 있다고 설명한다.

사용자가 이후 새로운 조건을 말하면
처음 선택한 조건을 잊지 말고 새로운 조건까지 합쳐서
추천 후보를 좁히거나 다시 추천한다.

예:
처음:
"애교가 많고 사람을 좋아하는 고양이"

이후:
"털이 많이 빠지는 건 싫어"

→ 처음 조건과 털 관리 조건을 모두 고려한다.

또한:
"아파트에서 키울 거야"
"조용한 고양이가 좋아"
"큰 고양이가 좋아"

등의 새로운 조건도 기존 조건에 추가해서 고려한다.

한국어로만 대답한다.
친근하고 귀엽게 대답한다.
답변 마지막 글자는 반드시 '냥'으로 끝낸다.
"""


# =========================================================
# 세션 상태
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_personality" not in st.session_state:
    st.session_state.selected_personality = []

if "selected_preferences" not in st.session_state:
    st.session_state.selected_preferences = []


# =========================================================
# 선택지
# =========================================================
personality_options = [
    "🏠 조용하고 차분한 편",
    "🎉 활발하고 노는 걸 좋아해",
    "💕 애교 많고 정이 많은 편",
    "🧘 혼자 있는 시간도 좋아해",
    "👀 호기심이 많아",
    "😌 느긋하고 여유로운 편"
]

preference_options = [
    "💕 사람을 잘 따르는 고양이",
    "🥰 애교가 많은 고양이",
    "⚡ 활발하고 장난기 많은 고양이",
    "🌙 차분하고 조용한 고양이",
    "🐾 독립적인 고양이",
    "✨ 털이 복슬복슬한 고양이",
    "🧹 털 관리가 쉬운 고양이",
    "🏡 집에서 편안하게 지내는 고양이",
    "🗣️ 사람과 상호작용을 좋아하는 고양이"
]


# =========================================================
# 처음 화면
# =========================================================
if len(st.session_state.messages) == 0:

    # -----------------------------------------------------
    # 성격
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">💭 내 성격</div>',
        unsafe_allow_html=True
    )

    # 2열 버튼
    cols = st.columns(2)

    for i, option in enumerate(personality_options):

        with cols[i % 2]:

            is_selected = option in st.session_state.selected_personality

            if is_selected:
                button_text = "✓ " + option
            else:
                button_text = option

            if st.button(
                button_text,
                key=f"personality_{i}",
                use_container_width=True
            ):

                if option in st.session_state.selected_personality:
                    st.session_state.selected_personality.remove(option)
                else:
                    st.session_state.selected_personality.append(option)

                st.rerun()


    # -----------------------------------------------------
    # 원하는 고양이
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">🐾 내가 원하는 고양이</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(2)

    for i, option in enumerate(preference_options):

        with cols[i % 2]:

            is_selected = option in st.session_state.selected_preferences

            if is_selected:
                button_text = "✓ " + option
            else:
                button_text = option

            if st.button(
                button_text,
                key=f"preference_{i}",
                use_container_width=True
            ):

                if option in st.session_state.selected_preferences:
                    st.session_state.selected_preferences.remove(option)
                else:
                    st.session_state.selected_preferences.append(option)

                st.rerun()


    # -----------------------------------------------------
    # 현재 선택한 조건
    # -----------------------------------------------------
    if (
        st.session_state.selected_personality
        or st.session_state.selected_preferences
    ):

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        selected_text = []

        if st.session_state.selected_personality:
            selected_text.append(
                "💭 "
                + ", ".join(st.session_state.selected_personality)
            )

        if st.session_state.selected_preferences:
            selected_text.append(
                "🐾 "
                + ", ".join(st.session_state.selected_preferences)
            )

        st.markdown(
            f"""
            <div class="chat-card">
                <b>✨ 내가 고른 조건</b><br><br>
                {"<br>".join(selected_text)}
            </div>
            """,
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # 추천 버튼
    # -----------------------------------------------------
    st.markdown(
        '<div class="recommend-button">',
        unsafe_allow_html=True
    )

    recommend = st.button(
        "🐱 이 조건으로 고양이 찾아줘냥!",
        use_container_width=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # 추천 실행
    # -----------------------------------------------------
    if recommend:

        if (
            not st.session_state.selected_personality
            and not st.session_state.selected_preferences
        ):

            st.warning(
                "성격이나 원하는 고양이 특징을 하나 이상 골라줘냥! 🐾"
            )

        else:

            personality = ", ".join(
                st.session_state.selected_personality
            )

            preferences = ", ".join(
                st.session_state.selected_preferences
            )

            first_message = f"""
내 성격:
{personality if personality else "선택하지 않음"}

내가 원하는 고양이:
{preferences if preferences else "선택하지 않음"}

이 조건을 모두 고려해서 나에게 잘 맞는 고양이 품종을
약 3마리 추천해줘.
각 고양이가 왜 잘 맞는지도 설명해줘.
"""

            st.session_state.messages.append({
                "role": "user",
                "content": first_message
            })

            try:

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        *st.session_state.messages
                    ]
                )

                answer = response.choices[0].message.content

                if not answer.endswith("냥"):
                    answer = answer.rstrip() + "냥"

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.rerun()

            except Exception:

                st.error(
                    "앗! 냥냥이가 잠깐 졸고 있어냥 😿 다시 눌러줘냥!"
                )


# =========================================================
# 대화 출력
# =========================================================
for message in st.session_state.messages:

    if message["role"] == "user":

        # 처음 조건 메시지는 너무 길게 보여주지 않음
        if len(message["content"]) > 200:

            st.markdown(
                """
                <div class="chat-card user-card">
                    <b>🙋 나</b><br><br>
                    처음 선택한 조건으로 고양이를 찾아줘냥! 🐾
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="chat-card user-card">
                    <b>🙋 나</b><br><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            f"""
            <div class="chat-card ai-card">
                <b>🐱 냥냥 AI</b><br><br>
                {message["content"].replace(chr(10), "<br>")}
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 추천 고양이 3마리 사진
# =========================================================
if len(st.session_state.messages) > 0:

    latest_answer = ""

    for message in reversed(st.session_state.messages):

        if message["role"] == "assistant":
            latest_answer = message["content"]
            break

    recommended = []

    for cat_name in CAT_IMAGES:

        if cat_name in latest_answer:
            recommended.append(cat_name)

    # 최대 3마리
    recommended = recommended[:3]

    if recommended:

        st.markdown(
            '<div class="section-title">🐾 추천 고양이</div>',
            unsafe_allow_html=True
        )

        for cat_name in recommended:

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True
            )

            # 이름
            st.markdown(
                f'<div class="result-name">🐱 {cat_name}</div>',
                unsafe_allow_html=True
            )

            # 특징
            st.markdown(
                f"""
                <div class="result-description">
                    {CAT_INFO[cat_name]}
                </div>
                """,
                unsafe_allow_html=True
            )

            # 사진
            st.image(
                CAT_IMAGES[cat_name],
                use_container_width=True
            )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


# =========================================================
# 추가 채팅
# =========================================================
if len(st.session_state.messages) > 0:

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#887593;
            font-size:16px;
            margin-top:30px;
            margin-bottom:10px;
        ">
            💬 더 구체적으로 말해주면 추천을 다시 좁혀줄게냥!
        </div>
        """,
        unsafe_allow_html=True
    )

    user_input = st.chat_input(
        "예: 털이 많이 빠지는 건 싫어 🐾"
    )

    if user_input:

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        try:

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    *st.session_state.messages
                ],
                stream=True
            )

            answer = ""

            placeholder = st.empty()

            for chunk in response:

                if chunk.choices:

                    content = chunk.choices[0].delta.content

                    if content:

                        answer += content

                        placeholder.markdown(
                            f"""
                            <div class="chat-card ai-card">
                                <b>🐱 냥냥 AI</b><br><br>
                                {answer}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            answer = answer.rstrip()

            if not answer.endswith("냥"):
                answer += "냥"

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()

        except Exception:

            st.error(
                "앗! 냥냥이가 잠깐 졸고 있어냥 😿 다시 말해줘냥!"
            )
