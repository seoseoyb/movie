# -----------------------------
# 귀여운 화면 디자인
# -----------------------------
st.markdown("""
<style>

/* 전체 화면 배경 */
.stApp {
    background: linear-gradient(135deg, #fff7fb, #f5f0ff, #fffaf0);
}

/* -----------------------------
   날아다니는 고양이
   ----------------------------- */
.cat {
    position: fixed;
    font-size: 42px;
    z-index: 0;
    pointer-events: none;
    opacity: 0.8;
}

/* 고양이 위치 + 움직임 */
.cat1 {
    top: 12%;
    left: -80px;
    animation: fly1 14s linear infinite;
}

.cat2 {
    top: 30%;
    left: -100px;
    font-size: 34px;
    animation: fly2 18s linear infinite;
    animation-delay: 3s;
}

.cat3 {
    top: 55%;
    left: -80px;
    font-size: 48px;
    animation: fly3 16s linear infinite;
    animation-delay: 6s;
}

.cat4 {
    top: 75%;
    left: -100px;
    font-size: 30px;
    animation: fly4 20s linear infinite;
    animation-delay: 1s;
}

/* 화면 왼쪽 → 오른쪽으로 날아가기 */
@keyframes fly1 {
    0% {
        transform: translateX(0) rotate(-10deg);
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
        transform: translateX(0) rotate(8deg);
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
   제목
   ----------------------------- */

.main-title {
    text-align: center;
    font-family: "Arial Rounded MT Bold", "Malgun Gothic", sans-serif;
    font-size: 52px;
    font-weight: 900;
    letter-spacing: -2px;
    color: #5d4a72;
    margin-top: 10px;
    margin-bottom: 8px;
}

/* 제목 밑 설명 */
.main-subtitle {
    text-align: center;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 18px;
    font-weight: 500;
    color: #806f91;
    margin-bottom: 30px;
}


/* -----------------------------
   챗봇 카드
   ----------------------------- */

[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.88);
    border-radius: 22px;
    padding: 10px;
    margin-bottom: 12px;
    box-shadow: 0 5px 18px rgba(100, 80, 120, 0.08);
}

/* 입력창 */
[data-testid="stChatInput"] {
    border-radius: 20px;
}


/* 내용이 고양이보다 위에 보이도록 */
[data-testid="stAppViewContainer"] {
    position: relative;
    z-index: 1;
}

header {
    background: transparent !important;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# 날아다니는 고양이 추가
# -----------------------------
st.markdown("""
<div class="cat cat1">🐈</div>
<div class="cat cat2">🐱</div>
<div class="cat cat3">🐈‍⬛</div>
<div class="cat cat4">😺</div>
""", unsafe_allow_html=True)
