import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(BASE_DIR)


import streamlit as st
from streamlit_folium import st_folium


from src.components.map_view import create_route_map
from src.api.geocoder import NaverGeocoder
from src.api.public_api import PublicStoreAPI

from src.core.commercial_analyzer import CommercialAnalyzer
from src.core.business_recommender import BusinessRecommender
from src.core.business_score import BusinessScore
from src.core.recommend_location import RecommendLocation

st.set_page_config(page_title="AI 상권 분석", page_icon="📍", layout="wide")


st.title("📍 AI 상권 분석 플랫폼")


# -------------------------
# 주소 입력
# -------------------------

address = st.text_input("📍 분석할 주소 입력", "서울특별시 양천구 신월동")


# -------------------------
# 분석 버튼
# -------------------------

if st.button("🚀 AI 상권 분석", type="primary"):

    geocoder = NaverGeocoder()

    result = geocoder.geocode(address)

    if result:

        st.success("좌표 변환 성공")

        st.write(result)

        # -------------------------
        # 공공데이터 상점 조회
        # -------------------------

        store_api = PublicStoreAPI()

        stores = store_api.get_stores(
            latitude=result["lat"], longitude=result["lng"], radius=500
        )

        #st.write("상점 데이터 개수:", len(stores))

        #if stores:
        #    st.write("샘플 데이터:")
        #    st.write(stores[0])
        # -------------------------
        # 지도 표시
        # -------------------------

        # -------------------------
        # 추천 업종 위치 찾기
        # -------------------------

        # -------------------------
        # AI 창업 추천 계산
        # -------------------------

        recommender = BusinessRecommender(stores)

        recommendation = recommender.recommend()



        # -------------------------
        # 추천 업종 위치 찾기
        # -------------------------

        recommended_categories = [
            name
            for name, count in recommendation["recommend"]
        ]


        finder = RecommendLocation(
            stores
        )


        recommended_stores = finder.find(
            recommended_categories
        )

        st.write(
            "🔥 추천 매장 수:",
            len(recommended_stores)
        )

        # -------------------------
        # 지도 표시
        # -------------------------

        map_obj = create_route_map(
            result["lat"],
            result["lng"],
            stores or [],
            recommended_stores
        )


        st_folium(
            map_obj,
            width=1200,
            height=700,
            returned_objects=[]
        )

        # -------------------------
        # 상권 분석
        # -------------------------

        if stores:

            analyzer = CommercialAnalyzer(stores)

            analysis = analyzer.analyze()

            st.subheader("📊 상권 분석 결과")

            col1, col2, col3 = st.columns(3)

            col1.metric("총 상점 수", analysis["total"])

            col2.metric("업종 다양성", len(analysis["categories"]))

            col3.metric("상권 점수", analysis["score"])

            st.subheader("📌 업종 분포")

            st.bar_chart(analysis["categories"])

            # -------------------------
            # AI 창업 추천
            # -------------------------

            st.subheader("🤖 AI 창업 추천")

            col1, col2 = st.columns(2)

            with col1:

                st.success("💰 추천 업종")

                for name, count in recommendation["recommend"]:

                    st.write(f"✅ {name} : {count}개")

            with col2:

                st.warning("⚠️ 경쟁 높은 업종")

                for name, count in recommendation["avoid"]:

                    st.write(f"❌ {name} : {count}개")

            st.info(recommendation.get("reason", "분석 결과"))

            # -------------------------
            # 업종별 창업 점수
            # -------------------------

            st.subheader("🏆 업종별 창업 점수")

            score_engine = BusinessScore(stores)

            scores = score_engine.calculate()

            for item in scores:

                score = item["점수"]

                if score >= 80:
                    icon = "🔥"

                elif score >= 60:
                    icon = "👍"

                else:
                    icon = "⚠️"

                st.write(
                    f"{icon} {item['업종']} "
                    f": {score}점 "
                    f"(현재 {item['매장수']}개)"
                )

        else:

            st.info("공공데이터 API 응답이 비어 있어 기준 위치만 표시됩니다.")

    else:

        st.error("주소를 찾을 수 없습니다.")
