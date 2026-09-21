import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ---------------------------------------------------------
# 1. 기본 설정
# ---------------------------------------------------------

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 어제의 박스오피스")
st.caption("영화진흥위원회(KOBIS) 일일 박스오피스")


# ---------------------------------------------------------
# 2. 어제 날짜 계산
# ---------------------------------------------------------
# 배포 서버의 시간이 한국 시간이 아닐 수 있으므로
# 서버의 현재 시간이 아니라 'Asia/Seoul' 기준으로 날짜를 계산합니다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()
yesterday_kst = today_kst - timedelta(days=1)

# KOBIS API가 요구하는 YYYYMMDD 형식으로 변환합니다.
target_date = yesterday_kst.strftime("%Y%m%d")

# 화면에는 사람이 읽기 좋은 날짜로 표시합니다.
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


# ---------------------------------------------------------
# 3. KOBIS API 설정
# ---------------------------------------------------------

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)


# ---------------------------------------------------------
# 4. Secrets에서 인증키 가져오기
# ---------------------------------------------------------
# Streamlit Cloud의 Secrets에 다음과 같이 KOBIS_KEY를 등록해야 합니다.
#
# [secrets]
# KOBIS_KEY = "발급받은_인증키"
#
# 실제 인증키는 코드에 작성하지 않습니다.

try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]
except Exception:
    st.error(
        "KOBIS_KEY를 찾을 수 없습니다.\n\n"
        "Streamlit Cloud의 앱 설정 → Secrets에서 "
        "KOBIS_KEY가 등록되어 있는지 확인해 주세요."
    )
    st.stop()


if not KOBIS_KEY:
    st.error(
        "KOBIS_KEY가 비어 있습니다.\n\n"
        "Streamlit Cloud의 Secrets에 올바른 KOBIS 인증키를 등록해 주세요."
    )
    st.stop()


# ---------------------------------------------------------
# 5. KOBIS API 호출
# ---------------------------------------------------------

params = {
    "key": KOBIS_KEY,
    "targetDt": target_date,
}

try:
    response = requests.get(
        API_URL,
        params=params,
        timeout=10,
    )

    # HTTP 통신 자체가 실패했는지 확인합니다.
    response.raise_for_status()

    data = response.json()

except requests.exceptions.RequestException as e:
    st.error(
        "KOBIS API 요청에 실패했습니다.\n\n"
        "다음 항목을 확인해 주세요.\n"
        "- 인터넷 연결 상태\n"
        "- KOBIS API 서버 상태\n"
        "- API 주소가 올바른지\n"
        "- Streamlit Cloud에서 외부 API 요청이 가능한지\n\n"
        f"오류 내용: {e}"
    )
    st.stop()

except ValueError:
    st.error(
        "KOBIS API의 응답을 JSON으로 읽을 수 없습니다.\n\n"
        "KOBIS API 서버 상태나 API 응답 내용을 확인해 주세요."
    )
    st.stop()


# ---------------------------------------------------------
# 6. KOBIS가 반환하는 API 오류 확인
# ---------------------------------------------------------
# 중요한 부분입니다.
# KOBIS는 인증키가 잘못되어도 HTTP 상태코드가 200일 수 있고,
# 대신 응답 안에 faultInfo를 넣어 보낼 수 있습니다.

if "faultInfo" in data:
    fault_info = data.get("faultInfo", {})

    error_message = (
        fault_info.get("message")
        or fault_info.get("message")
        or "KOBIS API에서 오류를 반환했습니다."
    )

    st.error(
        f"KOBIS API 오류가 발생했습니다.\n\n"
        f"오류 내용: {error_message}\n\n"
        "다음 항목을 확인해 주세요.\n"
        "- Streamlit Cloud의 Secrets에 KOBIS_KEY가 있는지\n"
        "- 인증키를 정확하게 입력했는지\n"
        "- 인증키가 아직 유효한지\n"
        "- KOBIS Open API 사용 설정에 문제가 없는지"
    )
    st.stop()


# ---------------------------------------------------------
# 7. 예상한 응답 구조인지 확인
# ---------------------------------------------------------

box_office_result = data.get("boxOfficeResult")

if not box_office_result:
    st.error(
        "KOBIS 응답에 boxOfficeResult가 없습니다.\n\n"
        "API 응답 형식이 예상과 다른 상태입니다. "
        "KOBIS API 상태와 요청 날짜를 확인해 주세요."
    )
    st.stop()


movie_list = box_office_result.get("dailyBoxOfficeList", [])


# ---------------------------------------------------------
# 8. 영화 목록이 비어 있는 경우
# ---------------------------------------------------------

if not movie_list:
    st.warning(
        f"{display_date}의 영화 목록이 비어 있습니다.\n\n"
        "다음 항목을 확인해 주세요.\n"
        "- KOBIS에서 해당 날짜의 일일 박스오피스가 집계되었는지\n"
        "- 조회 날짜(targetDt)가 YYYYMMDD 형식인지\n"
        "- KOBIS API 응답에 일일 박스오피스 데이터가 있는지\n"
        "- KOBIS 서버가 일시적으로 데이터를 제공하지 않는 상태인지"
    )
    st.stop()


# ---------------------------------------------------------
# 9. API 데이터를 표 형태로 변환
# ---------------------------------------------------------
# KOBIS API의 숫자 값은 문자열로 오므로
# 관객수와 스크린수 등은 숫자로 변환합니다.

rows = []

for movie in movie_list:
    rows.append(
        {
            "순위": int(movie.get("rank", 0)),
            "영화명": movie.get("movieNm", ""),
            "개봉일": movie.get("openDt", ""),
            "관객수": int(movie.get("audiCnt", 0)),
            "누적관객": int(movie.get("audiAcc", 0)),
            "스크린수": int(movie.get("scrnCnt", 0)),
        }
    )

df = pd.DataFrame(rows)


# ---------------------------------------------------------
# 10. 숫자를 보기 좋은 형태로 표시하기 위한 함수
# ---------------------------------------------------------

def format_number(value):
    """숫자에 천 단위 쉼표를 넣어 줍니다."""
    return f"{value:,}"


# ---------------------------------------------------------
# 11. 조회 날짜 표시
# ---------------------------------------------------------

st.subheader(f"📅 {display_date} 일일 박스오피스")

st.info(
    f"한국 시간(Asia/Seoul) 기준 어제인 {display_date}의 "
    "KOBIS 일일 박스오피스입니다."
)


# ---------------------------------------------------------
# 12. 1위 영화 지표 카드
# ---------------------------------------------------------

first_movie = df.iloc[0]

st.subheader(f"🏆 1위: {first_movie['영화명']}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="어제 관객수",
        value=f"{format_number(first_movie['관객수'])}명",
    )

with col2:
    st.metric(
        label="누적 관객수",
        value=f"{format_number(first_movie['누적관객'])}명",
    )

with col3:
    st.metric(
        label="스크린수",
        value=f"{format_number(first_movie['스크린수'])}개",
    )


# ---------------------------------------------------------
# 13. 관객수 상위 5편 막대그래프
# ---------------------------------------------------------

st.subheader("📊 관객수 상위 5편")

top5 = df.head(5).copy()

# 영화명을 그래프의 인덱스로 사용합니다.
chart_data = top5.set_index("영화명")[["관객수"]]

st.bar_chart(chart_data)


# ---------------------------------------------------------
# 14. 전체 박스오피스 표
# ---------------------------------------------------------

st.subheader("🎞️ 전체 순위")

display_df = df.copy()

# 표에서는 숫자를 천 단위 쉼표가 들어간 문자열로 보여 줍니다.
display_df["관객수"] = display_df["관객수"].map(format_number)
display_df["누적관객"] = display_df["누적관객"].map(format_number)
display_df["스크린수"] = display_df["스크린수"].map(format_number)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# 15. 출처 안내
# ---------------------------------------------------------

st.caption(
    "데이터 출처: 영화진흥위원회 영화관입장권통합전산망(KOBIS) "
    "일일 박스오피스 Open API"
)
