import os
import sys

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(BASE_DIR)


import streamlit as st
from streamlit_folium import st_folium
from dotenv import load_dotenv


# =========================================================
# 환경변수
# =========================================================

load_dotenv()


# =========================================================
# API / Core
# =========================================================

from src.api.geocoder import NaverGeocoder
from src.api.public_api import PublicStoreAPI
from src.api.legal_dong_api import LegalDongAPI

from src.components.map_view import create_route_map

from src.core.business_recommender import BusinessRecommender
from src.core.business_score import BusinessScore
from src.core.commercial_analyzer import CommercialAnalyzer
from src.core.recommend_location import RecommendLocation
from src.core.startup_location import StartupLocation


# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="AI 상권 분석 플랫폼",
    page_icon="📍",
    layout="wide"
)


# =========================================================
# 제목
# =========================================================

st.title("📍 AI 상권 분석 플랫폼")

st.caption(
    "공공데이터와 AI 알고리즘을 활용한 "
    "맞춤형 상권 분석 및 창업 추천 서비스"
)


# =========================================================
# 법정동 API 초기화
# =========================================================

try:

    legal_dong_api = LegalDongAPI()

except Exception as e:

    st.error(
        "❌ 법정동 API 설정 오류"
    )

    st.code(
        str(e)
    )

    st.info(
        "프로젝트 루트의 .env 파일에 "
        "DATA_GO_KR_SERVICE_KEY를 설정해주세요."
    )

    st.stop()


# =========================================================
# 전국 법정동 데이터 로드
# =========================================================

try:

    with st.spinner(
        "전국 법정동 데이터를 준비하는 중입니다..."
    ):

        sido_list = (
            legal_dong_api
            .get_sido_list()
        )

except Exception as e:

    st.error(
        "❌ 전국 법정동 데이터를 가져오지 못했습니다."
    )

    st.exception(e)

    st.stop()


if not sido_list:

    st.error(
        "법정동 데이터가 없습니다."
    )

    st.stop()


# =========================================================
# 검색 영역
# =========================================================

with st.container():

    col_sido, col_sigungu, col_dong, col_btn = st.columns(
        [2, 2, 2, 1.3],
        vertical_alignment="bottom"
    )

    # -----------------------------------------------------
    # 시/도
    # -----------------------------------------------------

    with col_sido:

        sido = st.selectbox(
            "시/도",
            sido_list,
            index=0,
            key="sido_select"
        )

    # -----------------------------------------------------
    # 시/군/구
    # -----------------------------------------------------

    sigungu_list = (
        legal_dong_api
        .get_sigungu_list(sido)
    )

    with col_sigungu:

        if sigungu_list:

            sigungu = st.selectbox(
                "시/군/구",
                sigungu_list,
                index=0,
                key="sigungu_select"
            )

        else:

            sigungu = ""

            st.selectbox(
                "시/군/구",
                ["(해당 없음)"],
                disabled=True,
                key="sigungu_empty"
            )

    # -----------------------------------------------------
    # 읍/면/동
    # -----------------------------------------------------

    dong_list = (
        legal_dong_api
        .get_dong_list(
            sido,
            sigungu
        )
    )

    with col_dong:

        if dong_list:

            dong = st.selectbox(
                "읍/면/동",
                dong_list,
                index=0,
                key="dong_select"
            )

        else:

            dong = ""

            st.selectbox(
                "읍/면/동",
                ["(해당 없음)"],
                disabled=True,
                key="dong_empty"
            )

    # -----------------------------------------------------
    # 분석 버튼
    # -----------------------------------------------------

    with col_btn:

        analyze_btn = st.button(
            "🚀 AI 상권 분석",
            type="primary",
            use_container_width=True
        )


# =========================================================
# 선택 주소
# =========================================================

address_parts = [
    sido,
    sigungu,
    dong
]

address = " ".join(
    part.strip()
    for part in address_parts
    if part and part.strip()
).strip()


# =========================================================
# 선택된 법정동 정보
# =========================================================

dong_info = None
legal_dong_code = None


if sido and sigungu and dong:

    dong_info = (
        legal_dong_api
        .get_dong_info(
            sido,
            sigungu,
            dong
        )
    )

    if dong_info:

        legal_dong_code = (
            dong_info["법정동코드"]
        )


# =========================================================
# 선택 주소 표시
# =========================================================

st.caption(
    f"📍 선택된 주소: **{address}**"
)


# 법정동 코드 표시
if legal_dong_code:

    st.caption(
        f"🏷️ 법정동코드: **{legal_dong_code}**"
    )


# =========================================================
# 분석 실행
# =========================================================

if analyze_btn:

    # -----------------------------------------------------
    # 주소 확인
    # -----------------------------------------------------

    if not address:

        st.error(
            "분석할 주소를 선택해주세요."
        )

        st.stop()

    # -----------------------------------------------------
    # 분석 시작
    # -----------------------------------------------------

    with st.spinner(
        "상권 데이터 수집 및 상세주소 분석을 진행 중입니다..."
    ):

        # =================================================
        # 1. Naver Geocoding
        # =================================================

        geocoder = NaverGeocoder()

        result = (
            geocoder
            .geocode(address)
        )

        if not result:

            st.error(
                "주소를 찾을 수 없습니다. "
                "선택한 법정동의 주소를 확인해주세요."
            )

            st.stop()


        # =================================================
        # 2. 공공데이터 상점 조회
        # =================================================

        store_api = PublicStoreAPI()

        stores = (
            store_api
            .get_stores(
                latitude=result["lat"],
                longitude=result["lng"],
                radius=500
            )
        )


        # =================================================
        # 3. AI 창업 추천
        # =================================================

        recommender = (
            BusinessRecommender(
                stores
            )
        )

        recommendation = (
            recommender
            .recommend()
        )


        # =================================================
        # 4. 추천 업종 위치 찾기
        # =================================================

        recommended_categories = [
            name
            for name, count
            in recommendation["recommend"]
        ]


        finder = RecommendLocation(
            stores
        )

        recommended_stores = (
            finder
            .find(
                recommended_categories
            )
        )


        # =================================================
        # 5. TOP5 창업 위치 분석
        # =================================================

        startup = StartupLocation(
            stores
        )

        startup_results = (
            startup
            .analyze()
        )

        top5 = startup_results[:5]


        # =================================================
        # 6. 추천 매장 상세주소 처리
        # =================================================

        for item in top5:

            shop = item.get(
                "추천매장",
                {}
            )


            # -------------------------------------------------
            # 1차: 공공데이터 주소 사용
            # -------------------------------------------------

            store_addr = (
                shop.get("rdnmAdr")
                or
                shop.get("lnoAdr")
            )


            if (
                store_addr
                and store_addr.strip()
            ):

                building_name = (
                    shop.get("bnoNm")
                    or
                    shop.get("bldNm")
                    or
                    ""
                )

                item["detail_address"] = (
                    f"{store_addr} "
                    f"{building_name}"
                ).strip()


            else:

                # ---------------------------------------------
                # 2차: 좌표 기반 역지오코딩
                # ---------------------------------------------

                lat = (
                    item.get("lat")
                    or
                    item.get("추천위도")
                    or
                    shop.get("lat")
                )

                lng = (
                    item.get("lng")
                    or
                    item.get("추천경도")
                    or
                    shop.get("lon")
                )


                if lat and lng:

                    item["detail_address"] = (
                        geocoder
                        .reverse_geocode(
                            float(lat),
                            float(lng)
                        )
                    )


                    # -----------------------------------------
                    # 역지오코딩 실패
                    # -----------------------------------------

                    if (
                        item["detail_address"]
                        == "주소 없음"
                    ):

                        item["detail_address"] = (
                            address
                        )

                else:

                    item["detail_address"] = (
                        address
                    )


    # =====================================================
    # 분석 결과
    # =====================================================

    st.divider()


    # =====================================================
    # 1. TOP 5 AI 추천 창업
    # =====================================================

    st.subheader(
        "🏆 AI 추천 창업 TOP 5"
    )


    top_cols = st.columns(5)


    for idx, (col, item) in enumerate(
        zip(top_cols, top5),
        1
    ):

        with col:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**Top {idx}**"
                )

                st.markdown(
                    f"### 🔥 {item['업종']}"
                )

                st.metric(
                    label="창업 점수",
                    value=f"{item['점수']}점"
                )

                st.caption(
                    f"🏪 현재 매장수: "
                    f"**{item['매장수']}개**"
                )

                st.markdown("---")

                st.markdown(
                    "📍 **추천 상세주소**"
                )

                st.info(
                    item.get(
                        "detail_address",
                        address
                    )
                )


    # =====================================================
    # 2. 지도 및 요약 대시보드
    # =====================================================

    st.subheader(
        "🗺️ 상권 입지 및 분석 지도"
    )


    map_obj = create_route_map(
        result["lat"],
        result["lng"],
        stores,
        recommended_stores,
        top5
    )


    st_folium(
        map_obj,
        use_container_width=True,
        height=500,
        returned_objects=[]
    )


    # =====================================================
    # 3. 상세 분석 탭
    # =====================================================

    st.write("")


    tab1, tab2, tab3 = st.tabs(
        [
            "📊 상권 현황",
            "🤖 AI 창업 진단",
            "🥇 전체 업종 평가"
        ]
    )


    # =====================================================
    # TAB 1
    # =====================================================

    with tab1:

        if stores:

            analyzer = (
                CommercialAnalyzer(
                    stores
                )
            )

            analysis = (
                analyzer
                .analyze()
            )


            m_col1, m_col2, m_col3 = (
                st.columns(3)
            )


            m_col1.metric(
                "총 반경 내 상점 수",
                f"{analysis['total']}개"
            )


            m_col2.metric(
                "업종 다양성",
                f"{len(analysis['categories'])}개"
            )


            m_col3.metric(
                "상권 활성화 점수",
                f"{analysis['score']}점"
            )


            st.markdown(
                "#### 📌 업종 분포 현황"
            )


            st.bar_chart(
                analysis["categories"]
            )


        else:

            st.info(
                "공공데이터 API 응답이 비어 있어 "
                "상세 상권 통계를 표시할 수 없습니다."
            )


    # =====================================================
    # TAB 2
    # =====================================================

    with tab2:

        if stores:

            st.info(
                f"💡 **분석 요약**: "
                f"{recommendation.get(
                    'reason',
                    '분석 결과가 생성되었습니다.'
                )}"
            )


            r_col1, r_col2 = (
                st.columns(2)
            )


            # -------------------------------------------------
            # 진입 추천 업종
            # -------------------------------------------------

            with r_col1:

                with st.container(
                    border=True
                ):

                    st.subheader(
                        "💰 진입 추천 업종"
                    )


                    for name, count in (
                        recommendation[
                            "recommend"
                        ]
                    ):

                        st.markdown(
                            f"✅ **{name}** "
                            f"(`현재 {count}개`)"
                        )


            # -------------------------------------------------
            # 경쟁 과열 업종
            # -------------------------------------------------

            with r_col2:

                with st.container(
                    border=True
                ):

                    st.subheader(
                        "⚠️ 경쟁 과열 업종"
                    )


                    for name, count in (
                        recommendation[
                            "avoid"
                        ]
                    ):

                        st.markdown(
                            f"❌ **{name}** "
                            f"(`현재 {count}개`)"
                        )


    # =====================================================
    # TAB 3
    # =====================================================

    with tab3:

        if stores:

            score_engine = (
                BusinessScore(
                    stores
                )
            )

            scores = (
                score_engine
                .calculate()
            )


            st.markdown(
                "#### 📋 전체 업종별 창업 적합도 점수"
            )


            s_col1, s_col2 = (
                st.columns(2)
            )


            for idx, item in enumerate(
                scores
            ):

                score = item["점수"]


                if score >= 80:

                    icon = "🔥"
                    badge = "높음"


                elif score >= 60:

                    icon = "👍"
                    badge = "보통"


                else:

                    icon = "⚠️"
                    badge = "주의"


                target_col = (
                    s_col1
                    if idx % 2 == 0
                    else s_col2
                )


                with target_col:

                    target_col.markdown(
                        f"{icon} "
                        f"**{item['업종']}** | "
                        f"`{score}점` "
                        f"({badge}) — "
                        f"현재 {item['매장수']}개"
                    )