import sys
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(BASE_DIR)


import streamlit as st
from streamlit_folium import st_folium


from src.components.map_view import create_route_map
from src.api.geocoder import NaverGeocoder
from src.api.public_api import PublicStoreAPI



st.set_page_config(
    page_title="AI 상권 분석",
    page_icon="📍",
    layout="wide"
)


st.title(
    "📍 AI 상권 분석 플랫폼"
)



address = st.text_input(
    "분석할 주소 입력",
    "서울특별시 양천구 신월동"
)



if st.button("지도 분석"):


    geocoder = NaverGeocoder()


    result = geocoder.geocode(
        address
    )


    if result:


        st.success(
            "좌표 변환 성공"
        )


        st.write(result)



        store_api = PublicStoreAPI()


        stores = store_api.get_stores(
            latitude=result["lat"],
            longitude=result["lng"],
            radius=500
        )

        map_obj = create_route_map(

            result["lat"],

            result["lng"],

            stores or []

        )



        st_folium(

            map_obj,

            width=1200,

            height=700,

            returned_objects=[]

        )



        if not stores:

            st.info(
                "공공데이터 API 응답이 비어 있어 기준 위치만 표시됩니다."
            )



    else:


        st.error(
            "주소를 찾을 수 없습니다."
        )