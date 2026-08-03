import requests
from typing import Optional, Dict

from config.settings import (
    NAVER_CLIENT_ID,
    NAVER_CLIENT_SECRET
)


GEOCODE_URL = (
    "https://maps.apigw.ntruss.com/"
    "map-geocode/v2/geocode"
)


class NaverGeocoder:
    """
    네이버 주소 -> 좌표 변환
    """

    def __init__(
        self,
        client_id=NAVER_CLIENT_ID,
        client_secret=NAVER_CLIENT_SECRET
    ):

        self.headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret
        }


    def geocode(
        self,
        address: str
    ) -> Optional[Dict]:

        queries = [
            address,
            f"{address} 서울",
            f"서울특별시 {address}"
        ]


        for query in queries:

            params = {
                "query": query
            }


            response = requests.get(
                GEOCODE_URL,
                headers=self.headers,
                params=params
            )


            if response.status_code != 200:

                print(
                    "Geocode Error:",
                    response.text
                )

                continue


            data = response.json()


            addresses = data.get(
                "addresses"
            )


            if addresses:

                result = addresses[0]


                return {
                    "address":
                        result.get(
                            "roadAddress"
                        ),

                    "jibunAddress":
                        result.get(
                            "jibunAddress"
                        ),

                    "lat":
                        float(
                            result["y"]
                        ),

                    "lng":
                        float(
                            result["x"]
                        )
                }


        return None