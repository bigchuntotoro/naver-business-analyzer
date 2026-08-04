import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import streamlit as st
from streamlit_folium import st_folium

from src.api.geocoder import NaverGeocoder
from src.api.public_api import PublicStoreAPI
from src.components.map_view import create_route_map
from src.core.business_recommender import BusinessRecommender
from src.core.business_score import BusinessScore
from src.core.commercial_analyzer import CommercialAnalyzer
from src.core.recommend_location import RecommendLocation
from src.core.startup_location import StartupLocation

# 페이지 설정
st.set_page_config(page_title="AI 상권 분석 플랫폼", page_icon="📍", layout="wide")

st.title("📍 AI 상권 분석 플랫폼")
st.caption("공공데이터와 AI 알고리즘을 활용한 맞춤형 상권 분석 및 창업 추천 서비스")

# -------------------------
# 검색 영역
# -------------------------
with st.container():
    col_input, col_btn = st.columns([4, 1], vertical_alignment="bottom")
    with col_input:
        address = st.text_input(
            "📍 분석할 주소 입력",
            "서울특별시 양천구 신월동",
            help="도로명 주소 또는 지번 주소를 입력하세요.",
        )
    with col_btn:
        analyze_btn = st.button(
            "🚀 AI 상권 분석", type="primary", use_container_width=True
        )

# -------------------------
# 분석 실행
# -------------------------
if analyze_btn:
    with st.spinner("상권 데이터 수집 및 상세주소 분석을 진행 중입니다..."):
        geocoder = NaverGeocoder()
        result = geocoder.geocode(address)

        if result:
            # 공공데이터 상점 조회
            store_api = PublicStoreAPI()
            stores = store_api.get_stores(
                latitude=result["lat"], longitude=result["lng"], radius=500
            )

            # AI 창업 추천 계산
            recommender = BusinessRecommender(stores)
            recommendation = recommender.recommend()

            # 추천 업종 위치 찾기
            recommended_categories = [
                name for name, count in recommendation["recommend"]
            ]
            finder = RecommendLocation(stores)
            recommended_stores = finder.find(recommended_categories)

            # -------------------------
            # TOP5 창업 위치 분석
            # -------------------------
            startup = StartupLocation(stores)
            startup_results = startup.analyze()
            top5 = startup_results[:5]

            # 🔥 상세주소 파싱 로직
            for item in top5:
                shop = item.get("추천매장", {})

                # 1. 공공데이터 매장의 도로명주소(rdnmAdr) 또는 지번주소(lnoAdr) 확인
                store_addr = shop.get("rdnmAdr") or shop.get("lnoAdr")

                if store_addr and store_addr.strip():
                    # 공공데이터 자체 주소 데이터가 있는 경우
                    building_name = shop.get("bnoNm") or shop.get("bldNm") or ""
                    item["detail_address"] = f"{store_addr} {building_name}".strip()
                else:
                    # 2. 주소가 비어있을 경우 좌표(lat/lng 또는 추천위도/추천경도) 기반 역지오코딩 수행
                    lat = item.get("lat") or item.get("추천위도") or shop.get("lat")
                    lng = item.get("lng") or item.get("추천경도") or shop.get("lon")

                    if lat and lng:
                        item["detail_address"] = geocoder.reverse_geocode(
                            float(lat), float(lng)
                        )
                        # NaverGeocoder 반환값이 '주소 없음'인 경우 원래 입력한 기본주소로 대체
                        if item["detail_address"] == "주소 없음":
                            item["detail_address"] = address
                    else:
                        item["detail_address"] = address

            st.divider()

            # -------------------------
            # 1. TOP 5 AI 추천 창업 (카드 출력)
            # -------------------------
            st.subheader("🏆 AI 추천 창업 TOP 5")

            top_cols = st.columns(5)
            for idx, (col, item) in enumerate(zip(top_cols, top5), 1):
                with col:
                    with st.container(border=True):
                        st.markdown(f"**Top {idx}**")
                        st.markdown(f"### 🔥 {item['업종']}")
                        st.metric(label="창업 점수", value=f"{item['점수']}점")
                        st.caption(f"🏪 현재 매장수: **{item['매장수']}개**")

                        # 📍 상세주소 표출
                        st.markdown("---")
                        st.markdown("📍 **추천 상세주소**")
                        st.info(f"{item['detail_address']}")

            # -------------------------
            # 2. 지도 및 요약 대시보드
            # -------------------------
            st.subheader("🗺️ 상권 입지 및 분석 지도")
            map_obj = create_route_map(
                result["lat"], result["lng"], stores, recommended_stores, top5
            )
            st_folium(
                map_obj, use_container_width=True, height=500, returned_objects=[]
            )

            # -------------------------
            # 3. 상세 분석 탭 구성
            # -------------------------
            st.write("")
            tab1, tab2, tab3 = st.tabs(
                ["📊 상권 현황", "🤖 AI 창업 진단", "🥇 전체 업종 평가"]
            )

            # TAB 1: 상권 현황
            with tab1:
                if stores:
                    analyzer = CommercialAnalyzer(stores)
                    analysis = analyzer.analyze()

                    m_col1, m_col2, m_col3 = st.columns(3)
                    m_col1.metric("총 반경 내 상점 수", f"{analysis['total']}개")
                    m_col2.metric("업종 다양성", f"{len(analysis['categories'])}개")
                    m_col3.metric("상권 활성화 점수", f"{analysis['score']}점")

                    st.markdown("#### 📌 업종 분포 현황")
                    st.bar_chart(analysis["categories"])
                else:
                    st.info(
                        "공공데이터 API 응답이 비어 있어 상세 상권 통계를 표시할 수 없습니다."
                    )

            # TAB 2: AI 창업 진단
            with tab2:
                if stores:
                    st.info(
                        f"💡 **분석 요약**: {recommendation.get('reason', '분석 결과가 생성되었습니다.')}"
                    )

                    r_col1, r_col2 = st.columns(2)
                    with r_col1:
                        with st.container(border=True):
                            st.subheader("💰 진입 추천 업종")
                            for name, count in recommendation["recommend"]:
                                st.markdown(f"✅ **{name}** (`현재 {count}개`) ")

                    with r_col2:
                        with st.container(border=True):
                            st.subheader("⚠️ 경쟁 과열 업종")
                            for name, count in recommendation["avoid"]:
                                st.markdown(f"❌ **{name}** (`현재 {count}개`) ")

            # TAB 3: 전체 업종 평가
            with tab3:
                if stores:
                    score_engine = BusinessScore(stores)
                    scores = score_engine.calculate()

                    st.markdown("#### 📋 전체 업종별 창업 적합도 점수")

                    s_col1, s_col2 = st.columns(2)
                    for idx, item in enumerate(scores):
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

                        target_col = s_col1 if idx % 2 == 0 else s_col2
                        with target_col:
                            target_col.markdown(
                                f"{icon} **{item['업종']}** | `{score}점` ({badge}) — 현재 {item['매장수']}개"
                            )
        else:
            st.error(
                "주소를 찾을 수 없습니다. 정확한 도로명 주소 또는 지번 주소를 입력해주세요."
            )
