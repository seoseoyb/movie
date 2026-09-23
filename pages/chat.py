import streamlit as st
from openai import OpenAI

# =========================================================
# 1. 페이지 기본 설정
# =========================================================
st.set_page_config(
    page_title="냥냥 고양이 추천소",
    page_icon="🐱",
    layout="wide"
)

# =========================================================
# 2. 고양이 사진
# =========================================================
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

# =========================================================
# 3. 전체 디자인
# =========================================================
st.markdown("""
<style>

.stApp {
    background:
        linear-gradient(
            135deg,
            #fff7fb 0%,
            #f5f0ff 50%,
            #fffaf0 100%
        );
}

/* 전체 여백 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* =========================
   날아다니는 고양이
   ========================= */

.flying-cat {
    position: fixed;
    font-size: 38px;
    z-index: 0;
    pointer-events: none;
    animation: fly 13s linear infinite;
    opacity: 0.8;
}

.cat1 {
    top: 12%;
    left: -80px;
    animation-delay: 0s;
}

.cat2 {
    top: 30%;
    left: -100px;
    animation-delay: 4s;
    font-size: 30px;
}

.cat3 {
    top: 55%;
    left: -100px;
    animation-delay: 8s;
    font-size: 45px;
}

.cat4 {
    top: 75%;
    left: -100px;
    animation-delay: 2s;
    font-size: 28px;
}

@keyframes fly {
    0% {
        transform: translateX(-100px) rotate(-8deg);
    }

    50% {
        transform: translateX(55vw) translateY(-35px) rotate(8deg);
    }

    100% {
        transform: translateX(110vw) translateY(10px) rotate(-5deg);
    }
}

/* =========================
   제목
   ========================= */

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

    margin-top: 10px;
    margin-bottom: 8px;
}

.sub-title {
    text-align: center;
    font-size: 18px;
    color: #887593;
    margin-bottom: 35px;
}

/* =========================
   선택 박스
   ========================= */

.choice-box {
    background: rgba(255, 255, 255, 0.78);
    border-radius: 25px;
    padding: 25px 30px;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(100, 70, 120, 0.08);
}

.choice-title {
    font-family:
        "Arial Rounded MT Bold",
        "Trebuchet MS",
        "Malgun Gothic",
        sans-serif;

    font-size: 25px;
    font-weight: 800;
    color: #604b73;
    margin-bottom: 10px;
}

/* =========================
   채팅 카드
   ========================= */

.chat-card {
    background: rgba(255, 255, 255, 0.82);
    border-radius: 22px;
    padding: 18px 22px;
    margin: 12px 0;
    box-shadow: 0 5px 18px rgba(90, 70, 100, 0.08);
}

.user-card {
    border-left: 5px solid #c9a7e8;
}

.ai-card {
    border-left: 5px solid #f0b6d5;
}

/* =========================
   추천 고양이 카드
   ========================= */

.cat-result {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 25px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 8px 25px rgba(90, 70, 100, 0.10);
}

.cat-result img {
    border-radius: 20px;
}

.cat-name {
    font-family:
        "Arial Rounded MT Bold",
        "Trebuchet MS",
        "Malgun Gothic",
        sans-serif;

    color: #604b73;
    font-size: 25px;
    font-weight: 800;
}

/* 버튼 */
.stButton > button {
    border-radius: 18px;
    border: none;
    padding: 12px 25px;
    font-size: 17px;
    font-weight: 700;
    background: #e8d4f5;
    color: #604b73;
}

.stButton > button:hover {
    background: #dcc1ee;
}

/* multiselect */
div[data-baseweb="select"] > div {
    border-radius: 16px !important;
    background-color: rgba(255,255,255,0.9) !important;
}

/* 채팅 입력창 */
div[data-testid="stChatInput"] {
    border-radius: 20px;
}

</style>

<!-- 날아다니는 고양이 -->
<div class="flying-cat cat1">🐱</div>
<div class="flying-cat cat2">🐈</div>
<div class="flying-cat cat3">😺</div>
<div class="flying-cat cat4">🐾</div>
""", unsafe_allow_html=True)

# =========================================================
# 4. 제목
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
# 5. Gemini 설정
# =========================================================
client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MODEL_NAME = "gemini-3.5-flash-lite"

# =========================================================
# 6. AI에게 전달할 시스템 프롬프트
# =========================================================
SYSTEM_PROMPT = """
너는 '냥냥 고양이 추천소'라는 고양이 품종 추천 AI다.

사용자가 처음 선택한 자신의 성격과 원하는 고양이 특징을 바탕으로
추가 질문을 하지 말고 바로 고양이를 추천한다.

사용자가 선택한 조건을 모두 기억한다.

처음 추천 이후에는 사용자가 새로운 조건을 말할 수 있다.
새로운 조건이 들어오면 이전 조건과 새로운 조건을 모두 합쳐서
추천 후보를 좁히거나 새로운 품종을 추천한다.

예:
사용자: 털이 많이 빠지는 건 싫어
→ 기존 조건 + 털 관리 조건을 반영해서 다시 추천

사용자: 좀 더 애교가 많았으면 좋겠어
→ 기존 조건 + 애교 조건을 반영해서 후보를 좁힘

사용자: 아파트에서 키울 거야
→ 기존 조건 + 생활환경까지 고려

중요:
- 사용자가 처음 선택한 조건만으로도 바로 추천한다.
- 처음부터 추가 질문을 여러 개 하지 않는다.
- 사용자가 새로운 조건을 말하면 이전 조건을 초기화하지 않는다.
- 이전 조건과 새로운 조건을 누적해서 생각한다.
- 필요하다면 2~3개의 품종을 비교해서 추천한다.
- 특정 품종의 성격을 절대적으로 단정하지 않는다.
- 같은 품종이어도 개체마다 성격이 다를 수 있음을 알려준다.
- 품종의 일반적인 경향과 실제 개체의 차이를 구분한다.

추천할 때는 다음 내용을 적절히 포함한다.

🐱 가장 잘 어울리는 고양이
💗 왜 잘 맞을까?
✨ 특징
⚠️ 알아둘 점
🐾 다른 후보

한국어로만 답한다.
친근하고 귀엽게 말한다.
답변의 마지막 글자는 반드시 '냥'으로 끝낸다.
"""

# =========================================================
# 7. 대화 기록 저장
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================================================
# 8. 처음 방문했을 때 선택 화면
# =========================================================
if len(st.session_state.messages) == 0:

    # -------------------------
    # 성격 선택
    # -------------------------
    st.markdown(
        '<div class="choice-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="choice-title">💭 나는 이런 성격이야</div>',
        unsafe_allow_html=True
    )

    personality_options = [
        "🏠 조용하고 차분한 편",
        "🎉 활발하고 노는 걸 좋아해",
        "💕 애교 많고 정이 많은 편",
        "🧘 혼자 있는 시간도 좋아해",
        "👀 호기심이 많아",
        "😌 느긋하고 여유로운 편"
    ]

    selected_personality = st.multiselect(
        "나에게 해당하는 것을 골라줘!",
        personality_options,
        placeholder="성격을 선택해줘냥 🐾",
        label_visibility="collapsed"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # 원하는 고양이 특징
    # -------------------------
    st.markdown(
        '<div class="choice-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="choice-title">🐾 이런 고양이를 원해</div>',
        unsafe_allow_html=True
    )

    cat_preference_options = [
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

    selected_preferences = st.multiselect(
        "원하는 특징을 골라줘!",
        cat_preference_options,
        placeholder="원하는 고양이 특징을 선택해줘냥 🐱",
        label_visibility="collapsed"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # 추천 버튼
    # -------------------------
    if st.button(
        "🐱 이 조건으로 고양이 찾아줘냥!",
        use_container_width=True
    ):

        if not selected_personality and not selected_preferences:
            st.warning("성격이나 원하는 고양이 특징을 하나 이상 골라줘냥! 🐾")

        else:

            personality_text = (
                ", ".join(selected_personality)
                if selected_personality
                else "특별히 선택하지 않음"
            )

            preference_text = (
                ", ".join(selected_preferences)
                if selected_preferences
                else "특별히 선택하지 않음"
            )

            user_message = f"""
내 성격:
{personality_text}

내가 원하는 고양이 특징:
{preference_text}

이 조건에 맞는 고양이를 바로 추천해줘.
"""

            # 대화 기록에 저장
            st.session_state.messages.append({
                "role": "user",
                "content": user_message
            })

            # AI에게 요청
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

                # 마지막이 냥으로 끝나지 않는 경우 보정
                if not answer.endswith("냥"):
                    answer = answer.rstrip() + "냥"

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.rerun()

            except Exception:
                # 사용자에게 복잡한 오류 메시지를 보여주지 않음
                st.error(
                    "앗, 냥냥 추천소가 잠깐 졸고 있어냥 😿 잠시 후 다시 눌러줘냥!"
                )

# =========================================================
# 9. 기존 대화 출력
# =========================================================
for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="chat-card user-card">
                <b>🙋 나</b><br><br>
                {message["content"].replace(chr(10), "<br>")}
            </div>
            """,
            unsafe_allow_html=True
        )

    elif message["role"] == "assistant":

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
# 10. 추천 고양이 사진
# =========================================================
# AI 답변에 등장한 품종 이름을 찾아서 사진을 보여줌
if len(st.session_state.messages) > 0:

    latest_answer = ""

    for message in reversed(st.session_state.messages):
        if message["role"] == "assistant":
            latest_answer = message["content"]
            break

    recommended_cats = []

    for cat_name in CAT_IMAGES:

        if cat_name in latest_answer:
            recommended_cats.append(cat_name)

    # 최대 3마리까지만 사진 표시
    recommended_cats = recommended_cats[:3]

    if recommended_cats:

        st.markdown(
            "### 🐾 냥냥이가 추천한 고양이",
            unsafe_allow_html=True
        )

        columns = st.columns(len(recommended_cats))

        for column, cat_name in zip(columns, recommended_cats):

            with column:

                st.markdown(
                    '<div class="cat-result">',
                    unsafe_allow_html=True
                )

                st.image(
                    CAT_IMAGES[cat_name],
                    use_container_width=True
                )

                st.markdown(
                    f'<div class="cat-name">🐱 {cat_name}</div>',
                    unsafe_allow_html=True
                )

                st.write(CAT_INFO[cat_name])

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )


# =========================================================
# 11. 추천 이후 추가 대화
# =========================================================
if len(st.session_state.messages) > 0:

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#887593;
            margin-top:25px;
            margin-bottom:10px;
            font-size:16px;
        ">
        💬 더 구체적인 조건을 말해주면 추천을 다시 좁혀줄게냥!
        </div>
        """,
        unsafe_allow_html=True
    )

    user_input = st.chat_input(
        "예: 털이 많이 빠지는 건 싫어냥 🐾"
    )

    if user_input:

        # 사용자 메시지 저장
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        try:

            # 전체 대화를 다시 AI에게 전달
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

            # 스트리밍으로 답변 표시
            full_answer = ""

            placeholder = st.empty()

            for chunk in response:

                if chunk.choices:

                    delta = chunk.choices[0].delta.content

                    if delta:
                        full_answer += delta

                        placeholder.markdown(
                            f"""
                            <div class="chat-card ai-card">
                                <b>🐱 냥냥 AI</b><br><br>
                                {full_answer}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # 마지막 글자를 냥으로 맞춤
            full_answer = full_answer.rstrip()

            if not full_answer.endswith("냥"):
                full_answer += "냥"

            # 최종 답변 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_answer
            })

            st.rerun()

        except Exception:

            st.error(
                "앗, 냥냥 추천소가 잠깐 졸고 있어냥 😿 잠시 후 다시 말해줘냥!"
            )
