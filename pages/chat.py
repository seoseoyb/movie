import streamlit as st
from openai import OpenAI

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="냥냥 고양이 추천소",
    page_icon="🐱",
    layout="wide"
)

# --------------------------------------------------
# 고양이가 날아다니는 배경 + 화면 디자인
# --------------------------------------------------

st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background: linear-gradient(
        135deg,
        #fff8fc 0%,
        #f8f2ff 50%,
        #eef9ff 100%
    );
}

/* 날아다니는 고양이 */
.flying-cat {
    position: fixed;
    font-size: 42px;
    z-index: 2;
    pointer-events: none;
    user-select: none;
}

/* 고양이 각각의 위치와 속도 */
.cat1 {
    top: 12%;
    left: -70px;
    animation: fly1 16s linear infinite;
}

.cat2 {
    top: 27%;
    right: -70px;
    animation: fly2 20s linear infinite;
}

.cat3 {
    top: 53%;
    left: -70px;
    animation: fly1 23s linear infinite;
    animation-delay: 4s;
}

.cat4 {
    top: 72%;
    right: -70px;
    animation: fly2 18s linear infinite;
    animation-delay: 2s;
}

.cat5 {
    top: 42%;
    left: -70px;
    animation: fly1 27s linear infinite;
    animation-delay: 8s;
}

/* 왼쪽 → 오른쪽 */
@keyframes fly1 {

    0% {
        transform: translateX(0) rotate(-8deg);
    }

    50% {
        transform:
            translateX(55vw)
            translateY(-35px)
            rotate(8deg);
    }

    100% {
        transform:
            translateX(110vw)
            translateY(10px)
            rotate(-8deg);
    }
}

/* 오른쪽 → 왼쪽 */
@keyframes fly2 {

    0% {
        transform: translateX(0) rotate(8deg);
    }

    50% {
        transform:
            translateX(-55vw)
            translateY(35px)
            rotate(-8deg);
    }

    100% {
        transform:
            translateX(-110vw)
            translateY(-10px)
            rotate(8deg);
    }
}

/* 메인 화면 */
[data-testid="stAppViewContainer"] {
    position: relative;
    z-index: 1;
}

/* 제목 */
.main-title {
    text-align: center;
    font-size: 43px;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 5px;
}

/* 부제목 */
.main-subtitle {
    text-align: center;
    font-size: 17px;
    color: #666666;
    margin-bottom: 30px;
}

/* 채팅 말풍선 */
[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 8px;
}

/* 입력창 */
[data-testid="stChatInput"] {
    border-radius: 20px;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.85);
}

</style>

<div class="flying-cat cat1">🐈</div>
<div class="flying-cat cat2">🐈‍⬛</div>
<div class="flying-cat cat3">🐱</div>
<div class="flying-cat cat4">😺</div>
<div class="flying-cat cat5">🐈</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 제목
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🐱 냥냥 고양이 추천소</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    '너의 성격과 원하는 고양이 스타일을 알려주면 어울리는 고양이를 찾아줄게냥'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# Gemini API 연결
# --------------------------------------------------

try:

    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

except Exception:

    client = None


# --------------------------------------------------
# AI의 역할을 정하는 시스템 프롬프트
# --------------------------------------------------

SYSTEM_PROMPT = """
너는 '냥냥 고양이 추천소'의 고양이 추천 AI야.

사용자의 성격, 생활 방식, 원하는 고양이 스타일을 파악한 뒤
그 사람에게 잘 어울릴 수 있는 고양이 품종이나 특성을 추천해주는 역할을 해.

[너의 역할]

사용자가 다음과 같은 정보를 말할 수 있어.

- 자신의 성격
- 집에서 보내는 시간
- 활동적인지 조용한지
- 원하는 고양이의 외모
- 털이 긴 고양이 / 짧은 고양이
- 애교가 많은 고양이
- 독립적인 고양이
- 활발한 고양이
- 조용한 고양이
- 큰 고양이 / 작은 고양이
- 털 빠짐에 대한 선호
- 고양이와 얼마나 놀아줄 수 있는지
- 고양이에게 기대하는 성격
- 기타 원하는 조건

이 정보를 종합해서 어울릴 수 있는 고양이를 추천해.

[추천 방법]

1. 먼저 사용자의 성격과 원하는 스타일을 파악해.

2. 정보가 부족하면 한 번에 질문 하나씩 물어봐.

3. 사용자가 말한 조건을 중요도에 따라 정리해.

4. 고양이의 품종 특성, 일반적인 성격, 활동량, 털 관리 등의
   정보를 바탕으로 추천해.

5. 특정 품종의 모든 고양이가 똑같은 성격을 가진다고 말하지 마.
   같은 품종이라도 개체마다 성격이 다를 수 있다는 점을 알려줘.

6. 단순히 외모만 보고 추천하지 말고
   사용자의 생활 방식과 성격을 함께 고려해.

7. 한 품종만 무조건 정답이라고 하지 말고
   필요하면 2~3개의 후보를 제시하고 각각 어떤 점이 잘 맞는지 설명해.

8. 사용자가 원하는 스타일과 실제 생활환경이 맞지 않는 경우에는
   그 차이도 친절하게 알려줘.

9. 고양이를 실제로 입양하는 상황이라면
   품종뿐 아니라 보호소나 구조묘 등 다양한 선택지가 있다는 점도
   필요할 때 알려줘.

10. 사용자가 아직 충분한 정보를 주지 않았다면
    성급하게 품종을 결정하지 마.

[말투]

- 중고등학생도 쉽게 이해할 수 있는 말로 설명해.
- 친근하고 귀엽게 말해.
- 반드시 한국어로만 답해.
- 너무 전문적인 표현은 쉽게 풀어서 설명해.
- 고양이를 좋아하는 친구처럼 자연스럽게 말해.
- 답변의 맨 마지막에는 반드시 '냥'을 붙여.
- 답변 중간에는 '냥'을 붙이지 마.
- '냥냥냥'처럼 반복해서 붙이지 마.
- 이미 마지막이 '냥'으로 끝났다면 다시 붙이지 마.

예시:

"오 너는 조용한 성격인데 고양이와는 가까이 지내고 싶은 편이구나냥"

"그렇다면 사람과 교감하는 걸 좋아하는 성향의 고양이를 먼저 살펴보는 게 좋겠어냥"

"외모까지 고려하면 브리티시 숏헤어와 랙돌을 후보로 볼 수 있어냥"

[추천 결과를 줄 때]

가능하면 다음과 같은 형식으로 설명해.

🐱 가장 잘 맞는 후보
품종:
잘 맞는 이유:

💗 이런 점이 잘 맞아
- 
- 
- 

⚠️ 미리 알아둘 점
- 
- 

🐾 다른 후보
- 품종 A: 어떤 사람에게 잘 맞는지
- 품종 B: 어떤 사람에게 잘 맞는지

단, 사용자의 정보가 부족하면 이 형식을 억지로 사용하지 말고
먼저 필요한 질문을 해.

그리고 어떤 상황에서도 답변의 마지막 글자는 반드시 '냥'이어야 해.
"""


# --------------------------------------------------
# 대화 기록 저장
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 사이드바
# --------------------------------------------------

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
    **성격**
    
    - 나는 조용한 편이야
    - 혼자 있는 시간이 많아
    - 활발하고 장난치는 걸 좋아해

    **원하는 고양이**

    - 털이 복슬복슬했으면 좋겠어
    - 애교 많은 고양이가 좋아
    - 너무 활동적인 고양이는 싫어
    - 큰 고양이가 좋아
    """)

    st.markdown("---")

    st.markdown(
        "🐱 **성격 + 생활환경 + 원하는 스타일을 "
        "알려줄수록 더 잘 추천할 수 있어!**"
    )


# --------------------------------------------------
# 이전 대화 표시
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# 사용자 입력
# --------------------------------------------------

user_input = st.chat_input(
    "나의 성격과 원하는 고양이를 말해줘!"
)


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

        answer_placeholder = st.empty()
        full_answer = ""

        try:

            if client is None:
                raise Exception("API 연결 실패")

            # 시스템 프롬프트 + 이전 대화 전달
            api_messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            api_messages.extend(
                st.session_state.messages
            )

            # Gemini에 스트리밍 요청
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=api_messages,
                stream=True
            )

            # 답변을 실시간으로 표시
            for chunk in response:

                if chunk.choices:

                    delta = chunk.choices[0].delta

                    if delta.content:

                        full_answer += delta.content

                        answer_placeholder.markdown(
                            full_answer + "▌"
                        )

            # 마지막 냥 처리
            full_answer = full_answer.rstrip()

            if full_answer and not full_answer.endswith("냥"):
                full_answer += "냥"

            # 최종 답변 표시
            answer_placeholder.markdown(
                full_answer
            )

            # 대화 기록에 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_answer
            })

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
