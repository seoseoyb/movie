import streamlit as st
from openai import OpenAI

# ==================================================
# 기본 설정
# ==================================================

st.set_page_config(
    page_title="냥냥 고양이 추천소",
    page_icon="🐱",
    layout="wide"
)


# ==================================================
# 고양이 사진 주소
# Wikimedia Commons의 공개 고양이 사진 사용
# ==================================================

CAT_IMAGES = {
    "랙돌": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Ragdoll%20Cat.jpg",
    "메인쿤": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Maine%20Coon%20%2812835%29.jpg",
    "샴": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Siamese%20cat.jpg",
    "브리티시 숏헤어": "https://commons.wikimedia.org/wiki/Special:Redirect/file/British%20Shorthair.jpg",
    "페르시안": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Persian%20cat.jpg",
    "러시안 블루": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Russian%20Blue.jpg",
}


# ==================================================
# 고양이 특징
# ==================================================

CAT_INFO = {

    "랙돌": {
        "emoji": "🤍",
        "feature": "차분하고 사람과 교감하는 것을 좋아하는 편으로 알려진 장모종이야.",
        "keyword": "차분함 · 애교 · 긴 털 · 사람과의 교감"
    },

    "메인쿤": {
        "emoji": "🩶",
        "feature": "몸집이 크고 털이 풍성하며 비교적 친근하고 사교적인 성향으로 알려져 있어.",
        "keyword": "대형묘 · 풍성한 털 · 사교적 · 장난기"
    },

    "샴": {
        "emoji": "💙",
        "feature": "사람과 상호작용하는 것을 좋아하고 활발하며 표현이 많은 편으로 알려져 있어.",
        "keyword": "활발함 · 표현력 · 교감 · 똑똑함"
    },

    "브리티시 숏헤어": {
        "emoji": "🩵",
        "feature": "차분하고 독립적인 성향을 보이는 경우가 많으며 짧고 빽빽한 털이 특징이야.",
        "keyword": "차분함 · 독립적 · 짧은 털 · 동글동글한 외모"
    },

    "페르시안": {
        "emoji": "🤍",
        "feature": "긴 털과 둥근 얼굴이 특징이며 비교적 차분한 성향으로 알려져 있어.",
        "keyword": "긴 털 · 차분함 · 조용함 · 복슬복슬"
    },

    "러시안 블루": {
        "emoji": "🩶",
        "feature": "은빛이 도는 짧은 털이 특징이며 조용하고 신중한 성향을 보이는 경우가 많아.",
        "keyword": "조용함 · 신중함 · 짧은 털 · 은빛 털"
    }
}


# ==================================================
# 배경 디자인
# ==================================================

st.markdown("""
<style>

.stApp {
    background:
        linear-gradient(
            135deg,
            #fff7fb 0%,
            #f5f1ff 50%,
            #eef9ff 100%
        );
}

/* 전체 화면에 떠다니는 고양이 */
.bg-cat {
    position: fixed;
    width: 85px;
    height: 85px;
    object-fit: cover;
    border-radius: 50%;
    opacity: 0.78;
    z-index: 0;
    pointer-events: none;
    box-shadow: 0 5px 20px rgba(0,0,0,0.12);
}

/* 고양이 위치 */
.bg-cat1 {
    top: 8%;
    left: 3%;
    animation: floating1 7s ease-in-out infinite;
}

.bg-cat2 {
    top: 20%;
    right: 4%;
    animation: floating2 9s ease-in-out infinite;
}

.bg-cat3 {
    bottom: 13%;
    left: 5%;
    animation: floating2 8s ease-in-out infinite;
}

.bg-cat4 {
    bottom: 8%;
    right: 5%;
    animation: floating1 10s ease-in-out infinite;
}

@keyframes floating1 {

    0% {
        transform: translateY(0px) rotate(-5deg);
    }

    50% {
        transform: translateY(-25px) rotate(5deg);
    }

    100% {
        transform: translateY(0px) rotate(-5deg);
    }
}

@keyframes floating2 {

    0% {
        transform: translateY(0px) rotate(5deg);
    }

    50% {
        transform: translateY(22px) rotate(-5deg);
    }

    100% {
        transform: translateY(0px) rotate(5deg);
    }
}

/* 메인 내용이 고양이보다 위에 오도록 */
[data-testid="stAppViewContainer"] {
    position: relative;
    z-index: 1;
}

/* 제목 */
.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: 800;
    margin-top: 15px;
    margin-bottom: 5px;
}

/* 부제목 */
.main-subtitle {
    text-align: center;
    font-size: 17px;
    color: #666666;
    margin-bottom: 30px;
}

/* 추천 카드 */
.cat-card {
    background: rgba(255, 255, 255, 0.93);
    border-radius: 22px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 6px 25px rgba(100, 80, 120, 0.12);
    border: 1px solid rgba(255,255,255,0.8);
}

.cat-card-title {
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 8px;
}

.cat-card-text {
    color: #555555;
    line-height: 1.7;
}

.cat-keyword {
    background: #f3edff;
    padding: 8px 12px;
    border-radius: 12px;
    display: inline-block;
    margin-top: 8px;
    font-size: 14px;
}

/* 채팅창 */
[data-testid="stChatMessage"] {
    border-radius: 18px;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.88);
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 배경 고양이
# ==================================================

st.markdown(f"""
<img class="bg-cat bg-cat1" src="{CAT_IMAGES['랙돌']}">
<img class="bg-cat bg-cat2" src="{CAT_IMAGES['메인쿤']}">
<img class="bg-cat bg-cat3" src="{CAT_IMAGES['브리티시 숏헤어']}">
<img class="bg-cat bg-cat4" src="{CAT_IMAGES['러시안 블루']}">
""", unsafe_allow_html=True)


# ==================================================
# 제목
# ==================================================

st.markdown(
    '<div class="main-title">🐱 냥냥 고양이 추천소</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    '내 성격과 원하는 고양이 스타일을 알려주면 '
    '찰떡같이 어울리는 고양이를 찾아줄게냥'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# Gemini API
# ==================================================

try:

    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

except Exception:

    client = None


# ==================================================
# AI 시스템 프롬프트
# ==================================================

SYSTEM_PROMPT = """
너는 '냥냥 고양이 추천소'의 고양이 추천 AI야.

사용자의 성격과 생활방식, 원하는 고양이의 외모와 성격을 파악해서
잘 어울릴 수 있는 고양이 품종을 추천해주는 역할을 해.

사용자가 알려줄 수 있는 정보:

- 자신의 성격
- 조용한지 활발한지
- 혼자 있는 것을 좋아하는지
- 사람과 많이 교감하고 싶은지
- 집에 있는 시간이 많은지
- 고양이와 놀아줄 수 있는 시간
- 원하는 털 길이
- 원하는 외모
- 원하는 크기
- 애교 많은 고양이를 원하는지
- 독립적인 고양이를 원하는지
- 활동적인 고양이를 원하는지
- 조용한 고양이를 원하는지
- 털 빠짐에 대한 선호

[추천 원칙]

1. 사용자의 성격과 원하는 고양이 스타일을 함께 고려해.

2. 정보가 부족하면 질문을 해.
   한 번에 너무 많은 질문을 하지 말고 자연스럽게 대화를 이어가.

3. 고양이 품종마다 일반적으로 알려진 특징을 설명하되,
   같은 품종이라도 개체마다 성격이 다를 수 있다는 점을 알려줘.

4. 외모만 보고 추천하지 마.

5. 사용자의 생활환경과 고양이의 활동량이나 관리 필요성을 함께 고려해.

6. 필요하다면 2~3개의 품종을 추천해.

7. 각 품종을 추천하는 이유를 사용자의 성격과 연결해서 설명해.

8. 추천 결과에는 반드시 품종의 정확한 한국어 이름을 사용해.

[추천 결과 형식]

추천할 정보가 충분해지면 다음처럼 정리해줘.

🐱 가장 잘 어울리는 고양이
품종: ○○

💗 왜 잘 맞을까?
사용자의 성격과 연결해서 설명

✨ 특징
- 특징 1
- 특징 2
- 특징 3

⚠️ 알아둘 점
- 주의할 점

🐾 다른 후보
- ○○
- ○○

단, 사용자의 정보가 충분하지 않다면 억지로 추천하지 말고
먼저 자연스럽게 질문해.

[말투]

- 친근하고 귀엽게 말해.
- 중고등학생도 쉽게 이해할 수 있게 설명해.
- 한국어로만 답해.
- 답변 마지막에는 반드시 '냥'을 붙여.
- 답변 중간에는 '냥'을 붙이지 마.
- 이미 마지막이 '냥'이면 중복해서 붙이지 마.
"""


# ==================================================
# 세션에 대화 저장
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==================================================
# 추천 결과를 화면에 보여주는 함수
# ==================================================

def show_cat_cards(text):

    # AI 답변에서 어떤 품종이 언급됐는지 찾기
    found_cats = []

    for breed in CAT_IMAGES.keys():

        if breed in text:
            if breed not in found_cats:
                found_cats.append(breed)

    # 최대 3개까지만 사진 표시
    found_cats = found_cats[:3]

    if not found_cats:
        return

    st.markdown("---")
    st.markdown("## 🐾 너에게 어울리는 고양이")

    # 추천 품종 수에 따라 컬럼 생성
    columns = st.columns(len(found_cats))

    for column, breed in zip(columns, found_cats):

        with column:

            st.image(
                CAT_IMAGES[breed],
                use_container_width=True
            )

            info = CAT_INFO[breed]

            st.markdown(
                f"""
                <div class="cat-card">

                <div class="cat-card-title">
                {info["emoji"]} {breed}
                </div>

                <div class="cat-card-text">
                {info["feature"]}
                </div>

                <div class="cat-keyword">
                {info["keyword"]}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# ==================================================
# 사이드바
# ==================================================

with st.sidebar:

    st.markdown("## 🐾 냥냥 고양이 추천소")

    if st.button(
        "🗑️ 대화 초기화",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.markdown("### 💡 이렇게 말해봐!")

    st.markdown("""
    **내 성격**

    나는 조용한 편이고 혼자 있는 것도 좋아해.

    **원하는 고양이**

    털이 복슬복슬하고 애교가 많았으면 좋겠어.

    **또는**

    나는 활동적인 성격이고
    고양이랑 많이 놀아주고 싶어.
    큰 고양이가 좋아!
    """)


# ==================================================
# 기존 대화 표시
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ==================================================
# 사용자 입력
# ==================================================

user_input = st.chat_input(
    "내 성격과 원하는 고양이를 말해줘!"
)


if user_input:

    # --------------------------------------------------
    # 사용자 메시지 저장
    # --------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)


    # --------------------------------------------------
    # AI 답변
    # --------------------------------------------------

    with st.chat_message("assistant"):

        answer_placeholder = st.empty()
        full_answer = ""

        try:

            if client is None:
                raise Exception("API 연결 실패")

            # 시스템 프롬프트
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

            # Gemini 호출
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=api_messages,
                stream=True
            )

            # AI 답변을 실시간으로 출력
            for chunk in response:

                if chunk.choices:

                    delta = chunk.choices[0].delta

                    if delta.content:

                        full_answer += delta.content

                        answer_placeholder.markdown(
                            full_answer + "▌"
                        )

            # 마지막에 냥 붙이기
            full_answer = full_answer.rstrip()

            if full_answer and not full_answer.endswith("냥"):
                full_answer += "냥"

            # 최종 답변
            answer_placeholder.markdown(
                full_answer
            )

            # 대화 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_answer
            })


            # --------------------------------------------------
            # 고양이 추천 사진 표시
            # --------------------------------------------------

            show_cat_cards(full_answer)


        except Exception:

            error_message = (
                "잠시 문제가 생겼어요. "
                "조금 후에 다시 시도해 주세요냥"
            )

            answer_placeholder.markdown(
                error_message
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })
