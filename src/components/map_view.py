import folium


def create_route_map(
    latitude,
    longitude,
    stores=None
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

        popup="분석 위치",

        icon=folium.Icon(
            color="red",
            icon="star"
        )

    ).add_to(m)



    # 상권 마커

    if stores:

        for store in stores:

            lat = store.get("lat")
            lon = store.get("lon")


            if lat is not None and lon is not None:

                folium.Marker(

                    [
                        float(lat),
                        float(lon)
                    ],

                    popup=store.get(
                        "bizesNm",
                        "상점"
                    ),

                    tooltip=store.get(
                        "bizesNm",
                        "상점"
                    ),

                    icon=folium.Icon(
                        color="blue"
                    )

                ).add_to(m)



    return m