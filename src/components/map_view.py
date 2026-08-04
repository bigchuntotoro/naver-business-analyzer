import folium


def create_route_map(
    latitude,
    longitude,
    stores=None,
    recommended=None
):

    m = folium.Map(
        location=[
            latitude,
            longitude
        ],
        zoom_start=15
    )


    # 분석 위치

    folium.Marker(
        [
            latitude,
            longitude
        ],
        popup="📍 분석 위치",
        icon=folium.Icon(
            color="red",
            icon="home"
        )
    ).add_to(m)



    # 일반 상점 표시

    for store in stores or []:

        lat = store.get("lat")
        lon = store.get("lon")


        if lat and lon:

            folium.Marker(
                [
                    lat,
                    lon
                ],
                popup=(
                    f"{store.get('bizesNm','상점')}<br>"
                    f"{store.get('indsMclsNm','')}"
                ),
                icon=folium.Icon(
                    color="blue",
                    icon="info-sign"
                )
            ).add_to(m)



    # ⭐ AI 추천 업종 표시

    for store in recommended or []:

        lat = store.get("lat")
        lon = store.get("lon")


        if lat and lon:

            folium.Marker(
                [
                    lat,
                    lon
                ],
                popup=(
                    "🔥 AI 추천 업종<br>"
                    f"{store.get('bizesNm','')}<br>"
                    f"{store.get('indsMclsNm','')}"
                ),
                icon=folium.Icon(
                    color="green",
                    icon="star"
                )
            ).add_to(m)


    return m