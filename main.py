import streamlit as st
import pandas as pd
import requests

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. Streamlit 기본 설정
# ============================================================
# 화면 제목, 아이콘, 넓은 화면 사용 여부를 설정합니다.

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide",
)


# ============================================================
# 2. 영화관 느낌의 배경 만들기
# ============================================================
# Streamlit 기본 배경 대신 어두운 영화관 느낌이 나도록
# CSS를 적용합니다.

st.markdown(
    """
    <style>
    /* 전체 앱 배경 */
    .stApp {
        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(90, 20, 20, 0.35),
                transparent 45%
            ),
            linear-gradient(
                180deg,
                #080808 0%,
                #111111 45%,
                #050505 100%
            );
        color: #f5f5f5;
    }

    /* 메인 콘텐츠의 가독성을 높입니다. */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* 제목 */
    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    h2, h3 {
        color: #f1f1f1 !important;
    }

    /* 안내 박스 */
    .stAlert {
        border-radius: 12px;
    }

    /* Metric 카드 */
    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            rgba(35, 35, 35, 0.95),
            rgba(15, 15, 15, 0.95)
        );
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35);
    }

    [data-testid="stMetricLabel"] {
        color: #bbbbbb !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    /* 표 */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* 영화관 느낌의 빨간 포인트 */
    .movie-theater-line {
        height: 4px;
        width: 100%;
        margin: 10px 0 25px 0;
        border-radius: 4px;
        background: linear-gradient(
            90deg,
            #8b0000,
            #ff3030,
            #8b0000
        );
    }

    /* 작은 설명 문구 */
    .movie-caption {
        color: #aaaaaa;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. 화면 제목
# ============================================================

st.title("🎬 어제의 박스오피스")

st.markdown(
    '<div class="movie-theater-line"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="movie-caption">'
    "영화진흥위원회(KOBIS) 일일 박스오피스"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# 4. 한국 시간 기준으로 날짜 계산
# ============================================================
# Streamlit Cloud 서버가 한국에 있지 않을 수 있기 때문에
# 서버의 현재 시간을 그대로 사용하지 않습니다.
#
# Asia/Seoul을 지정해서 한국 시간으로 오늘 날짜를 구한 뒤
# 하루를 빼서 '어제'를 계산합니다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()

yesterday_kst = today_kst - timedelta(days=1)

# KOBIS API가 요구하는 YYYYMMDD 형식입니다.
target_dt = yesterday_kst.strftime("%Y%m%d")

# 화면에 보여 줄 날짜입니다.
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


# ============================================================
# 5. 최근 10년 기준 날짜 계산
# ============================================================
# 여기서 말하는 '최근 10년 영화'는
# 어제 기준으로 최근 10년 안에 개봉한 영화입니다.
#
# 예를 들어 어제가 2026-09-20이라면
# 2016-09-20 이후 개봉한 영화를 대상으로 합니다.

ten_years_ago = yesterday_kst.replace(
    year=yesterday_kst.year - 10
)

ten_years_ago_text = ten_years_ago.strftime("%Y-%m-%d")


# ============================================================
# 6. 사이드바 옵션
# ============================================================

st.sidebar.header("🎞️ 조회 옵션")

recent_10_years_only = st.sidebar.checkbox(
    "최근 10년 이내 개봉작만 보기",
    value=False,
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "날짜는 한국 시간(Asia/Seoul)을 기준으로 자동 계산됩니다."
)

if recent_10_years_only:
    st.sidebar.info(
        f"개봉일이 {ten_years_ago_text} 이후인 "
        "영화만 표시합니다."
    )


# ============================================================
# 7. KOBIS API 주소
# ============================================================

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)


# ============================================================
# 8. Secrets에서 인증키 가져오기
# ============================================================
# 인증키를 코드에 직접 적으면 안 됩니다.
#
# Streamlit Cloud의 Settings → Secrets에 다음과 같이 등록합니다.
#
# KOBIS_KEY = "본인의_인증키"
#
# 실제 인증키는 main.py에 들어가지 않습니다.

try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]

except Exception:
    st.error(
        "🔑 KOBIS_KEY를 찾을 수 없습니다.\n\n"
        "Streamlit Cloud의 Settings → Secrets를 열고 "
        "다음 항목을 확인해 주세요.\n\n"
        "• KOBIS_KEY가 등록되어 있는지\n"
        "• 이름이 정확히 KOBIS_KEY인지\n"
        "• 인증키 값이 비어 있지 않은지"
    )

    st.stop()


# 인증키가 빈 문자열인 경우도 확인합니다.
if not str(KOBIS_KEY).strip():
    st.error(
        "🔑 KOBIS_KEY가 비어 있습니다.\n\n"
        "Streamlit Cloud의 Secrets에 "
        "유효한 KOBIS 인증키를 등록해 주세요."
    )

    st.stop()


# ============================================================
# 9. KOBIS API 요청
# ============================================================

params = {
    "key": KOBIS_KEY,
    "targetDt": target_dt,
}


try:
    response = requests.get(
        API_URL,
        params=params,
        timeout=10,
    )

    # HTTP 오류가 있으면 여기서 예외가 발생합니다.
    response.raise_for_status()

except requests.exceptions.Timeout:
    st.error(
        "⏱️ KOBIS API 요청 시간이 초과되었습니다.\n\n"
        "다음 항목을 확인해 주세요.\n\n"
        "• 인터넷 연결 상태\n"
        "• KOBIS API 서버 상태\n"
        "• 잠시 후 다시 실행"
    )

    st.stop()

except requests.exceptions.RequestException as error:
    st.error(
        "❌ KOBIS API 요청에 실패했습니다.\n\n"
        "다음 항목을 확인해 주세요.\n\n"
        "• 인터넷 연결 상태\n"
        "• KOBIS API 주소\n"
        "• KOBIS API 서버 상태\n"
        "• Streamlit Cloud의 외부 인터넷 접속 상태\n\n"
        f"상세 오류: {error}"
    )

    st.stop()


# ============================================================
# 10. JSON 응답으로 변환
# ============================================================

try:
    data = response.json()

except ValueError:
    st.error(
        "❌ KOBIS API 응답을 JSON으로 읽을 수 없습니다.\n\n"
        "KOBIS 서버가 예상하지 못한 응답을 보냈을 수 있습니다.\n"
        "잠시 후 다시 실행해 주세요."
    )

    st.stop()


# ============================================================
# 11. KOBIS API 자체 오류 확인
# ============================================================
# 중요합니다.
#
# KOBIS는 인증키가 잘못되어도 HTTP 상태코드 200을 반환할 수
# 있으므로 response.raise_for_status()만으로는 부족합니다.
#
# 따라서 응답 JSON에 faultInfo가 있는지도 확인합니다.

if "faultInfo" in data:

    fault_info = data.get("faultInfo", {})

    # KOBIS 오류 메시지를 가져옵니다.
    error_message = (
        fault_info.get("message")
        or fault_info.get("errorMessage")
        or "KOBIS API에서 오류를 반환했습니다."
    )

    st.error(
        "🚨 KOBIS API 오류가 발생했습니다.\n\n"
        f"오류 내용: {error_message}\n\n"
        "다음 항목을 확인해 주세요.\n\n"
        "• Streamlit Cloud의 Secrets에 KOBIS_KEY가 있는지\n"
        "• KOBIS_KEY의 이름이 정확한지\n"
        "• 인증키 값이 정확한지\n"
        "• 인증키가 유효한지\n"
        "• KOBIS Open API 사용 상태에 문제가 없는지"
    )

    st.stop()


# ============================================================
# 12. boxOfficeResult 확인
# ============================================================

box_office_result = data.get("boxOfficeResult")

if not box_office_result:
    st.error(
        "⚠️ KOBIS 응답에 boxOfficeResult가 없습니다.\n\n"
        "API 응답이 예상한 형식과 다릅니다.\n\n"
        "다음 항목을 확인해 주세요.\n\n"
        "• KOBIS API 서버 상태\n"
        "• KOBIS 인증키 상태\n"
        "• 조회 날짜\n"
        "• KOBIS API 응답 형식"
    )

    st.stop()


# ============================================================
# 13. 영화 목록 가져오기
# ============================================================

movie_list = box_office_result.get(
    "dailyBoxOfficeList",
    []
)


# ============================================================
# 14. 영화 목록이 비어 있는 경우
# ============================================================

if not movie_list:
    st.warning(
        f"📭 {display_date}의 영화 목록이 없습니다.\n\n"
        "다음 항목을 확인해 주세요.\n\n"
        "• KOBIS에서 해당 날짜의 일일 박스오피스가 집계되었는지\n"
        "• KOBIS API가 해당 날짜의 데이터를 제공하는지\n"
        "• KOBIS API 서버에 일시적인 문제가 없는지\n"
        "• 잠시 후 다시 실행해 보기"
    )

    st.stop()


# ============================================================
# 15. API 데이터를 DataFrame으로 변환
# ============================================================
# KOBIS의 숫자 데이터는 문자열로 들어옵니다.
# 따라서 int()를 이용해서 숫자로 변환합니다.

rows = []

for movie in movie_list:

    # 순위
    try:
        rank = int(movie.get("rank", 0))
    except (ValueError, TypeError):
        rank = 0

    # 관객수
    try:
        audi_cnt = int(movie.get("audiCnt", 0))
    except (ValueError, TypeError):
        audi_cnt = 0

    # 누적관객
    try:
        audi_acc = int(movie.get("audiAcc", 0))
    except (ValueError, TypeError):
        audi_acc = 0

    # 스크린수
    try:
        scrn_cnt = int(movie.get("scrnCnt", 0))
    except (ValueError, TypeError):
        scrn_cnt = 0

    rows.append(
        {
            "순위": rank,
            "영화명": movie.get("movieNm", ""),
            "개봉일": movie.get("openDt", ""),
            "관객수": audi_cnt,
            "누적관객": audi_acc,
            "스크린수": scrn_cnt,
        }
    )


df = pd.DataFrame(rows)


# ============================================================
# 16. DataFrame이 비어 있는지 확인
# ============================================================

if df.empty:
    st.warning(
        "📭 영화 데이터를 만들지 못했습니다.\n\n"
        "KOBIS API 응답에 영화 정보가 정상적으로 들어왔는지 "
        "확인해 주세요."
    )

    st.stop()


# ============================================================
# 17. 최근 10년 영화 필터
# ============================================================
# 체크박스를 선택한 경우에만 실행됩니다.
#
# openDt(개봉일)를 날짜로 바꾼 뒤
# 어제 기준 최근 10년 이내 영화만 남깁니다.

if recent_10_years_only:

    # 잘못된 날짜가 있어도 앱 전체가 멈추지 않도록
    # errors="coerce"를 사용합니다.
    df["개봉일_날짜"] = pd.to_datetime(
        df["개봉일"],
        errors="coerce",
    )

    df = df[
        df["개봉일_날짜"].notna()
        & (df["개봉일_날짜"].dt.date >= ten_years_ago)
        & (df["개봉일_날짜"].dt.date <= yesterday_kst)
    ].copy()

    # 화면에서는 임시 날짜 컬럼을 보여 주지 않습니다.
    if "개봉일_날짜" in df.columns:
        df = df.drop(columns=["개봉일_날짜"])


# ============================================================
# 18. 필터 결과가 비어 있는 경우
# ============================================================

if df.empty:

    st.warning(
        "📭 최근 10년 이내 개봉작 조건에 맞는 영화가 없습니다.\n\n"
        "KOBIS 일일 박스오피스에서 반환된 영화 중 "
        "최근 10년 이내 개봉작이 없는 경우입니다.\n\n"
        "사이드바에서 '최근 10년 이내 개봉작만 보기'를 "
        "해제하면 전체 순위를 볼 수 있습니다."
    )

    st.stop()


# ============================================================
# 19. 순위 기준으로 정렬
# ============================================================

df = df.sort_values(
    "순위",
    ascending=True,
).reset_index(drop=True)


# ============================================================
# 20. 조회 날짜 표시
# ============================================================

st.subheader(f"📅 {display_date} 박스오피스")

if recent_10_years_only:

    st.info(
        f"한국 시간 기준 {display_date}의 일일 박스오피스 중 "
        f"{ten_years_ago_text} 이후 개봉한 영화만 표시합니다."
    )

else:

    st.info(
        f"한국 시간 기준 {display_date}의 "
        "KOBIS 일일 박스오피스입니다."
    )


# ============================================================
# 21. 1위 영화 찾기
# ============================================================

first_movie = df.iloc[0]

st.subheader(
    f"🏆 1위 — {first_movie['영화명']}"
)


# ============================================================
# 22. 1위 영화의 지표 카드 3개
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        label="어제 관객수",
        value=f"{first_movie['관객수']:,}명",
    )


with col2:
    st.metric(
        label="누적 관객수",
        value=f"{first_movie['누적관객']:,}명",
    )


with col3:
    st.metric(
        label="스크린수",
        value=f"{first_movie['스크린수']:,}개",
    )


# ============================================================
# 23. 관객수 상위 3편 직선그래프
# ============================================================
# 사용자가 요청한 대로 상위 3편만 선 그래프로 표시합니다.
#
# 영화별 관객수를 한 번에 비교하기 위한 그래프입니다.

st.subheader("📈 관객수 상위 3편")

top3 = (
    df.sort_values(
        "관객수",
        ascending=False,
    )
    .head(3)
    .copy()
)

# 영화명을 인덱스로 설정합니다.
line_chart_data = top3.set_index("영화명")[["관객수"]]

st.line_chart(
    line_chart_data,
    y="관객수",
    use_container_width=True,
)


# ============================================================
# 24. 전체 박스오피스 표
# ============================================================

st.subheader("🎞️ 전체 순위")


# 원본 데이터는 숫자 형태로 유지하고,
# 화면 표시용 데이터만 따로 만듭니다.

display_df = df.copy()


# 숫자를 천 단위 쉼표로 표시합니다.
display_df["관객수"] = display_df["관객수"].map(
    lambda value: f"{value:,}"
)

display_df["누적관객"] = display_df["누적관객"].map(
    lambda value: f"{value:,}"
)

display_df["스크린수"] = display_df["스크린수"].map(
    lambda value: f"{value:,}"
)


# 사용자가 요청한 컬럼만 표시합니다.
display_df = display_df[
    [
        "순위",
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수",
    ]
]


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# 25. 데이터 출처
# ============================================================

st.caption(
    "데이터 출처: 영화진흥위원회 영화관입장권통합전산망(KOBIS) "
    "일일 박스오피스 Open API"
)
