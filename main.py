import streamlit as st
import pandas as pd
import requests

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. Streamlit 기본 설정
# ============================================================

st.set_page_config(
    page_title="오늘의 영화관",
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
                rgba(120, 15, 15, 0.35),
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

    .movie-card {
        background: rgba(25, 25, 25, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .movie-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
    }

    .movie-info {
        color: #aaaaaa;
        font-size: 0.9rem;
        margin-top: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. 제목
# ============================================================

st.title("🎬 오늘의 영화관")

st.markdown(
    '<div class="movie-line"></div>',
    unsafe_allow_html=True,
)

st.caption(
    "영화진흥위원회(KOBIS) 영화관입장권통합전산망"
)


# ============================================================
# 4. 한국 시간 기준으로 '어제' 계산
# ============================================================
# Streamlit Cloud 서버가 한국 시간이 아닐 수 있으므로
# 반드시 Asia/Seoul을 사용합니다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()

yesterday_kst = today_kst - timedelta(days=1)

target_dt = yesterday_kst.strftime("%Y%m%d")

display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


# ============================================================
# 5. Secrets에서 KOBIS 인증키 가져오기
# ============================================================
# 인증키를 코드에 직접 작성하지 않습니다.
#
# Streamlit Cloud:
#
# Settings → Secrets
#
# KOBIS_KEY = "본인의_KOBIS_인증키"

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
        "KOBIS 인증키를 등록해 주세요."
    )
    st.stop()


# ============================================================
# 6. KOBIS API 주소
# ============================================================

DAILY_BOXOFFICE_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

MOVIE_LIST_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "movie/searchMovieList.json"
)

MOVIE_INFO_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "movie/searchMovieInfo.json"
)


# ============================================================
# 7. KOBIS API 공통 요청 함수
# ============================================================

def request_kobis(url, params):
    """
    KOBIS API를 호출하는 공통 함수입니다.

    HTTP 오류뿐 아니라 KOBIS가 응답으로 보내는
    faultInfo도 확인합니다.
    """

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15,
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

    # KOBIS는 인증키가 틀려도 HTTP 200을 반환할 수 있으므로
    # JSON 안의 faultInfo를 반드시 확인합니다.
    if "faultInfo" in data:

        fault_info = data.get(
            "faultInfo",
            {},
        )

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
# 8. 어제의 박스오피스
# ============================================================

st.header(f"🍿 {display_date} 박스오피스")

try:

    daily_data = request_kobis(
        DAILY_BOXOFFICE_URL,
        {
            "key": KOBIS_KEY,
            "targetDt": target_dt,
        },
    )

except RuntimeError as error:

    st.error(
        "❌ 어제의 박스오피스를 가져오지 못했습니다.\n\n"
        f"{error}\n\n"
        "확인할 사항:\n"
        "• KOBIS_KEY가 정확한지\n"
        "• Streamlit Cloud Secrets 설정\n"
        "• KOBIS API 서버 상태\n"
        "• 인터넷 연결 상태"
    )

    daily_data = None


# ============================================================
# 9. 박스오피스 데이터 처리
# ============================================================

if daily_data:

    daily_result = daily_data.get(
        "boxOfficeResult",
        {},
    )

    daily_movies = daily_result.get(
        "dailyBoxOfficeList",
        [],
    )

    if not daily_movies:

        st.warning(
            f"📭 {display_date}의 박스오피스 데이터가 없습니다.\n\n"
            "KOBIS에서 해당 날짜의 일일 박스오피스가 "
            "집계되었는지 확인해 주세요."
        )

    else:

        daily_rows = []

        for movie in daily_movies:

            # 숫자 데이터는 KOBIS에서 문자열로 오므로
            # 화면에서 사용하기 전에 숫자로 변환합니다.

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
                    "영화명": movie.get(
                        "movieNm",
                        "",
                    ),
                    "개봉일": movie.get(
                        "openDt",
                        "",
                    ),
                    "관객수": audi_cnt,
                    "누적관객": audi_acc,
                    "스크린수": scrn_cnt,
                }
            )

        daily_df = pd.DataFrame(
            daily_rows
        )

        daily_df = daily_df.sort_values(
            "순위"
        ).reset_index(drop=True)


        # ====================================================
        # 10. 1위 영화 카드
        # ====================================================

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


        # ====================================================
        # 11. 관객수 상위 3편 직선그래프
        # ====================================================

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

        chart_df = top3.set_index(
            "영화명"
        )[["관객수"]]

        st.line_chart(
            chart_df,
            y="관객수",
            use_container_width=True,
        )


        # ====================================================
        # 12. 전체 박스오피스 표
        # ====================================================

        st.subheader("🎞️ 전체 순위")

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
# 13. 구분선
# ============================================================

st.markdown("---")


# ============================================================
# 14. 영화 검색
# ============================================================

st.header("🔎 영화 검색")

st.caption(
    "KOBIS에 등록된 영화 정보를 영화명으로 검색합니다."
)


search_word = st.text_input(
    "영화명을 입력하세요",
    placeholder="예: 아바타, 기생충, 인셉션",
)


# 검색 버튼
search_button = st.button(
    "🔍 영화 검색",
    type="primary",
)


# ============================================================
# 15. 영화 검색 실행
# ============================================================

if search_button:

    if not search_word.strip():

        st.warning(
            "검색할 영화명을 입력해 주세요."
        )

    else:

        try:

            movie_list_data = request_kobis(
                MOVIE_LIST_URL,
                {
                    "key": KOBIS_KEY,
                    "movieNm": search_word.strip(),
                    "itemPerPage": "20",
                },
            )

            movie_list_result = (
                movie_list_data
                .get(
                    "movieListResult",
                    {},
                )
            )

            search_movies = (
                movie_list_result
                .get(
                    "movieList",
                    [],
                )
            )

        except RuntimeError as error:

            st.error(
                "❌ 영화 검색에 실패했습니다.\n\n"
                f"{error}\n\n"
                "KOBIS_KEY와 API 상태를 확인해 주세요."
            )

            search_movies = []


        if not search_movies:

            st.warning(
                f"'{search_word}'에 해당하는 영화를 "
                "찾지 못했습니다.\n\n"
                "영화 제목의 일부만 입력하거나 "
                "다른 제목으로 검색해 보세요."
            )

        else:

            st.success(
                f"{len(search_movies)}개의 영화를 찾았습니다."
            )


            # 검색 결과를 보기 좋은 표로 만듭니다.
            search_rows = []

            for movie in search_movies:

                genres = movie.get(
                    "genreAlt",
                    "",
                )

                nations = movie.get(
                    "nationAlt",
                    "",
                )

                search_rows.append(
                    {
                        "영화명": movie.get(
                            "movieNm",
                            "",
                        ),
                        "영문명": movie.get(
                            "movieNmEn",
                            "",
                        ),
                        "개봉일": movie.get(
                            "openDt",
                            "",
                        ),
                        "대표장르": genres,
                        "대표국가": nations,
                        "영화코드": movie.get(
                            "movieCd",
                            "",
                        ),
                    }
                )

            search_df = pd.DataFrame(
                search_rows
            )

            st.dataframe(
                search_df[
                    [
                        "영화명",
                        "영문명",
                        "개봉일",
                        "대표장르",
                        "대표국가",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# 16. 장르별 영화 추천
# ============================================================

st.markdown("---")

st.header("🍿 장르로 영화 찾기")

st.caption(
    "원하는 장르를 선택하면 KOBIS에 등록된 "
    "해당 장르의 영화를 찾아 보여줍니다."
)


genre_options = [
    "액션",
    "어드벤처",
    "애니메이션",
    "코미디",
    "범죄",
    "다큐멘터리",
    "드라마",
    "가족",
    "판타지",
    "공포",
    "미스터리",
    "로맨스",
    "SF",
    "스릴러",
    "전쟁",
    "음악",
    "역사",
    "기타",
]


selected_genre = st.selectbox(
    "원하는 장르를 선택하세요",
    genre_options,
)


recommend_button = st.button(
    "🎬 이 장르 영화 찾아보기"
)


# ============================================================
# 17. 장르 검색
# ============================================================
# KOBIS의 영화목록 API에 genreNm을 전달합니다.
#
# 여기서는 KOBIS의 영화 데이터를 기준으로
# 해당 장르에 속하는 영화를 보여줍니다.

if recommend_button:

    try:

        genre_data = request_kobis(
            MOVIE_LIST_URL,
            {
                "key": KOBIS_KEY,
                "genreNm": selected_genre,
                "itemPerPage": "20",
            },
        )

        genre_result = (
            genre_data
            .get(
                "movieListResult",
                {},
            )
        )

        genre_movies = (
            genre_result
            .get(
                "movieList",
                [],
            )
        )

    except RuntimeError as error:

        st.error(
            "❌ 장르 검색에 실패했습니다.\n\n"
            f"{error}\n\n"
            "KOBIS_KEY와 API 상태를 확인해 주세요."
        )

        genre_movies = []


    if not genre_movies:

        st.warning(
            f"'{selected_genre}' 장르의 영화를 찾지 못했습니다.\n\n"
            "다른 장르를 선택해 보세요."
        )

    else:

        st.subheader(
            f"🎥 {selected_genre} 영화 추천"
        )

        st.caption(
            "아래 목록은 개인 취향을 예측한 추천 점수가 아니라, "
            "KOBIS 영화정보에서 해당 장르로 조회된 영화 목록입니다."
        )


        # ====================================================
        # 18. 추천 영화 표시
        # ====================================================

        recommendation_rows = []

        for movie in genre_movies:

            recommendation_rows.append(
                {
                    "영화명": movie.get(
                        "movieNm",
                        "",
                    ),
                    "영문명": movie.get(
                        "movieNmEn",
                        "",
                    ),
                    "개봉일": movie.get(
                        "openDt",
                        "",
                    ),
                    "장르": movie.get(
                        "genreAlt",
                        "",
                    ),
                    "국가": movie.get(
                        "nationAlt",
                        "",
                    ),
                }
            )


        recommendation_df = pd.DataFrame(
            recommendation_rows
        )


        st.dataframe(
            recommendation_df[
                [
                    "영화명",
                    "영문명",
                    "개봉일",
                    "장르",
                    "국가",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# 19. 안내
# ============================================================

st.markdown("---")

st.caption(
    "데이터 출처: 영화진흥위원회 영화관입장권통합전산망(KOBIS) Open API"
)
