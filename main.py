import streamlit as st
import pandas as pd
import requests

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. Streamlit 기본 설정
# ============================================================

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide",
)


# ============================================================
# 2. 영화관 느낌의 화면 디자인
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(120, 20, 20, 0.35),
                transparent 45%
            ),
            linear-gradient(
                180deg,
                #070707 0%,
                #111111 45%,
                #050505 100%
            );
        color: #f5f5f5;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        color: #ffffff !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            rgba(40, 40, 40, 0.95),
            rgba(12, 12, 12, 0.95)
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

    .movie-line {
        height: 4px;
        width: 100%;
        margin: 10px 0 28px 0;
        border-radius: 4px;
        background: linear-gradient(
            90deg,
            #700000,
            #ff3030,
            #700000
        );
    }

    .section-note {
        color: #aaaaaa;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. 제목
# ============================================================

st.title("🎬 어제의 박스오피스")

st.markdown(
    '<div class="movie-line"></div>',
    unsafe_allow_html=True,
)

st.caption(
    "영화진흥위원회(KOBIS) 영화관입장권통합전산망"
)


# ============================================================
# 4. 한국 시간 계산
# ============================================================
# Streamlit Cloud 서버가 한국 시간이 아닐 수 있으므로
# 반드시 Asia/Seoul을 사용합니다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()

yesterday_kst = today_kst - timedelta(days=1)

# KOBIS API용 날짜
yesterday_text = yesterday_kst.strftime("%Y%m%d")

# 화면 표시용 날짜
yesterday_display = yesterday_kst.strftime("%Y년 %m월 %d일")


# ============================================================
# 5. 최근 10년의 시작 날짜
# ============================================================
# '어제'를 기준으로 정확히 10년 전 날짜를 구합니다.
#
# 예:
# 어제가 2026-09-20이면
# 2016-09-20 ~ 2026-09-20을 조회합니다.

ten_year_start = yesterday_kst.replace(
    year=yesterday_kst.year - 10
)


# ============================================================
# 6. Secrets에서 KOBIS 인증키 가져오기
# ============================================================
# 인증키를 코드에 절대 적지 않습니다.
#
# Streamlit Cloud:
# Settings → Secrets
#
# KOBIS_KEY = "본인의_인증키"

try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]

except Exception:
    st.error(
        "🔑 KOBIS_KEY를 찾을 수 없습니다.\n\n"
        "Streamlit Cloud의 Settings → Secrets에서 "
        "KOBIS_KEY가 등록되어 있는지 확인해 주세요."
    )
    st.stop()


if not str(KOBIS_KEY).strip():
    st.error(
        "🔑 KOBIS_KEY가 비어 있습니다.\n\n"
        "Streamlit Cloud Secrets에 유효한 "
        "KOBIS 인증키를 입력해 주세요."
    )
    st.stop()


# ============================================================
# 7. API 주소
# ============================================================

DAILY_API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

WEEKLY_API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchWeeklyBoxOfficeList.json"
)


# ============================================================
# 8. KOBIS API 공통 요청 함수
# ============================================================

def request_kobis(url, params):
    """
    KOBIS API를 호출하고 JSON을 반환합니다.

    초보자를 위해:
    - HTTP 오류
    - JSON 오류
    - KOBIS의 faultInfo 오류
    를 각각 확인합니다.
    """

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "KOBIS API 요청 시간이 초과되었습니다."
        )

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"KOBIS API 요청에 실패했습니다: {error}"
        )

    try:
        data = response.json()

    except ValueError:
        raise RuntimeError(
            "KOBIS API 응답을 JSON으로 읽을 수 없습니다."
        )

    # KOBIS는 인증키가 틀려도 HTTP 200을 반환할 수 있습니다.
    # 따라서 반드시 faultInfo도 확인합니다.
    if "faultInfo" in data:

        fault_info = data.get("faultInfo", {})

        message = (
            fault_info.get("message")
            or fault_info.get("errorMessage")
            or "KOBIS API에서 오류를 반환했습니다."
        )

        raise RuntimeError(
            f"KOBIS API 오류: {message}"
        )

    return data


# ============================================================
# 9. 어제의 일일 박스오피스 가져오기
# ============================================================

st.subheader(f"📅 {yesterday_display} 일일 박스오피스")


try:

    daily_data = request_kobis(
        DAILY_API_URL,
        {
            "key": KOBIS_KEY,
            "targetDt": yesterday_text,
        },
    )

except RuntimeError as error:

    st.error(
        "❌ 어제의 박스오피스를 가져오지 못했습니다.\n\n"
        f"{error}\n\n"
        "다음 항목을 확인해 주세요.\n"
        "• KOBIS_KEY가 정확한지\n"
        "• Streamlit Cloud Secrets 설정\n"
        "• KOBIS API 서버 상태\n"
        "• 인터넷 연결 상태"
    )

    st.stop()


# ============================================================
# 10. 일일 박스오피스 목록 확인
# ============================================================

daily_result = daily_data.get(
    "boxOfficeResult",
    {}
)

daily_movies = daily_result.get(
    "dailyBoxOfficeList",
    []
)


if not daily_movies:

    st.warning(
        f"📭 {yesterday_display}의 영화 목록이 없습니다.\n\n"
        "KOBIS에서 해당 날짜의 박스오피스가 "
        "정상적으로 집계되었는지 확인해 주세요."
    )

else:

    # --------------------------------------------------------
    # 11. 일일 데이터를 DataFrame으로 변환
    # --------------------------------------------------------

    daily_rows = []

    for movie in daily_movies:

        try:
            rank = int(movie.get("rank", 0))
        except (ValueError, TypeError):
            rank = 0

        try:
            audi_cnt = int(movie.get("audiCnt", 0))
        except (ValueError, TypeError):
            audi_cnt = 0

        try:
            audi_acc = int(movie.get("audiAcc", 0))
        except (ValueError, TypeError):
            audi_acc = 0

        try:
            scrn_cnt = int(movie.get("scrnCnt", 0))
        except (ValueError, TypeError):
            scrn_cnt = 0

        daily_rows.append(
            {
                "순위": rank,
                "영화명": movie.get("movieNm", ""),
                "개봉일": movie.get("openDt", ""),
                "관객수": audi_cnt,
                "누적관객": audi_acc,
                "스크린수": scrn_cnt,
            }
        )

    daily_df = pd.DataFrame(daily_rows)

    daily_df = daily_df.sort_values(
        "순위"
    ).reset_index(drop=True)


    # ========================================================
    # 12. 1위 영화 카드
    # ========================================================

    first_movie = daily_df.iloc[0]

    st.subheader(
        f"🏆 1위 — {first_movie['영화명']}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "어제 관객수",
            f"{first_movie['관객수']:,}명",
        )

    with col2:
        st.metric(
            "누적 관객수",
            f"{first_movie['누적관객']:,}명",
        )

    with col3:
        st.metric(
            "스크린수",
            f"{first_movie['스크린수']:,}개",
        )


    # ========================================================
    # 13. 관객수 상위 3편 직선그래프
    # ========================================================

    st.subheader("📈 관객수 상위 3편")

    top3 = (
        daily_df
        .sort_values(
            "관객수",
            ascending=False,
        )
        .head(3)
        .copy()
    )

    chart_df = top3.set_index("영화명")[["관객수"]]

    st.line_chart(
        chart_df,
        y="관객수",
        use_container_width=True,
    )


    # ========================================================
    # 14. 어제 전체 순위표
    # ========================================================

    st.subheader("🎞️ 어제 전체 순위")

    display_daily = daily_df.copy()

    display_daily["관객수"] = (
        display_daily["관객수"]
        .map(lambda x: f"{x:,}")
    )

    display_daily["누적관객"] = (
        display_daily["누적관객"]
        .map(lambda x: f"{x:,}")
    )

    display_daily["스크린수"] = (
        display_daily["스크린수"]
        .map(lambda x: f"{x:,}")
    )

    st.dataframe(
        display_daily[
            [
                "순위",
                "영화명",
                "개봉일",
                "관객수",
                "누적관객",
                "스크린수",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 15. 구분선
# ============================================================

st.markdown("---")


# ============================================================
# 16. 최근 10년 박스오피스
# ============================================================

st.header("🏆 최근 10년간 영화 순위 총합")

st.markdown(
    '<div class="section-note">'
    "어제 기준 최근 10년 동안의 주간 박스오피스 관객수를 "
    "영화별로 합산한 순위입니다."
    "</div>",
    unsafe_allow_html=True,
)

st.info(
    f"조회 기간: "
    f"{ten_year_start.strftime('%Y-%m-%d')} ~ "
    f"{yesterday_kst.strftime('%Y-%m-%d')}"
)


# ============================================================
# 17. 10년 데이터 생성 함수
# ============================================================
# 주간 박스오피스 API를 이용합니다.
#
# weekGb = 0
# → 월요일~일요일 주간 박스오피스
#
# 최근 10년은 약 522주이므로 약 522회의 API 요청이
# 필요합니다.
#
# st.cache_data를 사용해서 최초 생성 후에는
# Streamlit이 결과를 캐시합니다.

@st.cache_data(
    ttl=60 * 60 * 24,
    show_spinner=False,
)
def build_ten_year_ranking(
    api_key,
    start_date,
    end_date,
):
    """
    최근 10년의 주간 박스오피스를 모아서
    영화별 관객수를 합산합니다.

    중요한 점:
    KOBIS 주간 API가 제공하는 weeklyBoxOfficeList에
    등장한 영화만 집계합니다.
    """

    current_date = start_date

    movie_totals = {}

    progress_dates = []

    # --------------------------------------------------------
    # 주간 조회 날짜 만들기
    # --------------------------------------------------------
    #
    # 주간 API의 targetDt는 해당 주간의 날짜를 지정합니다.
    # 안전하게 월요일 단위로 맞춥니다.

    monday = current_date - timedelta(
        days=current_date.weekday()
    )

    while monday <= end_date:

        progress_dates.append(monday)

        monday += timedelta(days=7)


    total_weeks = len(progress_dates)

    progress_bar = st.progress(0)

    status_text = st.empty()


    # --------------------------------------------------------
    # 각 주간 데이터 조회
    # --------------------------------------------------------

    for index, week_date in enumerate(progress_dates):

        target_dt = week_date.strftime("%Y%m%d")

        status_text.text(
            f"10년 데이터 수집 중... "
            f"{index + 1:,} / {total_weeks:,}주"
        )

        try:

            data = request_kobis(
                WEEKLY_API_URL,
                {
                    "key": api_key,
                    "targetDt": target_dt,
                    "weekGb": "0",
                },
            )

        except RuntimeError:
            # 한 주의 데이터에 문제가 있어도
            # 전체 작업을 바로 중단하지 않습니다.
            #
            # 단, 실제 데이터가 빠지는 것을 숨기지 않기 위해
            # 마지막에 수집 실패 주차를 표시합니다.

            index += 1

            progress_bar.progress(
                min(
                    index / total_weeks,
                    1.0,
                )
            )

            continue


        result = data.get(
            "boxOfficeResult",
            {}
        )

        weekly_movies = result.get(
            "weeklyBoxOfficeList",
            []
        )


        # ----------------------------------------------------
        # 영화별 관객수 합산
        # ----------------------------------------------------

        for movie in weekly_movies:

            movie_cd = movie.get(
                "movieCd"
            )

            movie_nm = movie.get(
                "movieNm",
                "",
            )

            if not movie_cd:
                # 영화 코드가 없으면 동일 영화명이
                # 중복 집계될 수 있으므로 건너뜁니다.
                continue


            try:
                audi_cnt = int(
                    movie.get(
                        "audiCnt",
                        0,
                    )
                )

            except (ValueError, TypeError):
                audi_cnt = 0


            # 영화가 처음 등장한 경우
            if movie_cd not in movie_totals:

                movie_totals[movie_cd] = {
                    "영화코드": movie_cd,
                    "영화명": movie_nm,
                    "개봉일": movie.get(
                        "openDt",
                        "",
                    ),
                    "10년간 관객수": 0,
                    "마지막 순위": None,
                }


            # 해당 주의 관객수를 누적합니다.
            movie_totals[movie_cd][
                "10년간 관객수"
            ] += audi_cnt


            # 가장 최근에 관측된 순위 저장
            try:
                movie_totals[movie_cd][
                    "마지막 순위"
                ] = int(
                    movie.get(
                        "rank",
                        0,
                    )
                )

            except (ValueError, TypeError):
                pass


        progress_bar.progress(
            (index + 1) / total_weeks
        )


    # --------------------------------------------------------
    # 진행 표시 제거
    # --------------------------------------------------------

    progress_bar.empty()
    status_text.empty()


    # --------------------------------------------------------
    # DataFrame 생성
    # --------------------------------------------------------

    result_df = pd.DataFrame(
        list(movie_totals.values())
    )


    if result_df.empty:
        return result_df


    # --------------------------------------------------------
    # 개봉일 처리
    # --------------------------------------------------------

    result_df["개봉일_날짜"] = pd.to_datetime(
        result_df["개봉일"],
        errors="coerce",
    )


    # --------------------------------------------------------
    # 최근 10년 이내 개봉 영화만 남김
    # --------------------------------------------------------

    result_df = result_df[
        result_df["개봉일_날짜"].notna()
        & (
            result_df["개봉일_날짜"].dt.date
            >= start_date
        )
        & (
            result_df["개봉일_날짜"].dt.date
            <= end_date
        )
    ].copy()


    # --------------------------------------------------------
    # 관객수 기준으로 순위 정렬
    # --------------------------------------------------------

    result_df = result_df.sort_values(
        "10년간 관객수",
        ascending=False,
    ).reset_index(drop=True)


    # 1위부터 새로운 순위를 붙입니다.
    result_df.insert(
        0,
        "순위",
        range(
            1,
            len(result_df) + 1,
        ),
    )


    return result_df


# ============================================================
# 18. 10년 데이터 불러오기
# ============================================================
# 버튼을 눌렀을 때만 무거운 10년 데이터 수집을 시작합니다.
#
# 앱을 새로 열 때마다 약 500회 API 요청이 발생하는 것을
# 막기 위한 장치입니다.

if "ten_year_loaded" not in st.session_state:
    st.session_state.ten_year_loaded = False


if st.button(
    "🎞️ 최근 10년 순위 불러오기",
    type="primary",
):

    st.session_state.ten_year_loaded = True


if st.session_state.ten_year_loaded:

    try:

        ten_year_df = build_ten_year_ranking(
            KOBIS_KEY,
            ten_year_start,
            yesterday_kst,
        )

    except Exception as error:

        st.error(
            "❌ 최근 10년 데이터를 가져오지 못했습니다.\n\n"
            f"상세 오류: {error}\n\n"
            "다음 항목을 확인해 주세요.\n"
            "• KOBIS_KEY가 정확한지\n"
            "• KOBIS API 사용량/제한\n"
            "• KOBIS 서버 상태\n"
            "• 네트워크 연결 상태"
        )

        st.stop()


    # ========================================================
    # 19. 10년 데이터가 없는 경우
    # ========================================================

    if ten_year_df.empty:

        st.warning(
            "📭 최근 10년 순위 데이터를 만들 수 없습니다.\n\n"
            "KOBIS 주간 박스오피스 API에서 데이터가 "
            "정상적으로 반환되는지 확인해 주세요."
        )

    else:

        # ====================================================
        # 20. 10년 순위 표
        # ====================================================

        st.success(
            f"총 {len(ten_year_df):,}편의 영화를 확인했습니다."
        )

        display_ten_year = ten_year_df.copy()


        display_ten_year[
            "10년간 관객수"
        ] = (
            display_ten_year[
                "10년간 관객수"
            ]
            .map(lambda x: f"{x:,}")
        )


        # 사용자가 요청한 10년 데이터 표입니다.
        st.dataframe(
            display_ten_year[
                [
                    "순위",
                    "영화명",
                    "개봉일",
                    "10년간 관객수",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=700,
        )


        # ====================================================
        # 21. 설명
        # ====================================================

        st.caption(
            "※ 10년간 관객수는 KOBIS 주간 박스오피스 API의 "
            "주간 관객수를 영화별로 합산한 값입니다. "
            "KOBIS 주간 API에서 해당 주의 박스오피스 목록에 "
            "포함된 기록을 기준으로 집계합니다."
        )


# ============================================================
# 22. 출처
# ============================================================

st.markdown("---")

st.caption(
    "데이터 출처: 영화진흥위원회 영화관입장권통합전산망(KOBIS) "
    "Open API"
)
