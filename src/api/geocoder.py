import requests
from typing import Optional, Dict

from config.settings import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

GEOCODE_URL = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"
REVERSE_GEOCODE_URL = "https://maps.apigw.ntruss.com/map-reversegeocode/v2/gc"


class NaverGeocoder:
    """
    네이버 주소 <-> 좌표 변환 클래스
    """

    def __init__(self, client_id=NAVER_CLIENT_ID, client_secret=NAVER_CLIENT_SECRET):
        self.headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
        }

    def geocode(self, address: str) -> Optional[Dict]:
        queries = [address, f"{address} 서울", f"서울특별시 {address}"]

        for query in queries:
            params = {"query": query}
            response = requests.get(GEOCODE_URL, headers=self.headers, params=params)

            if response.status_code != 200:
                print("Geocode Error:", response.text)
                continue

            data = response.json()
            addresses = data.get("addresses")

            if addresses:
                result = addresses[0]
                return {
                    "address": result.get("roadAddress"),
                    "jibunAddress": result.get("jibunAddress"),
                    "lat": float(result["y"]),
                    "lng": float(result["x"]),
                }
        return None

    def reverse_geocode(self, lat: float, lng: float) -> str:
        params = {
            "coords": f"{lng},{lat}",  # lng,lat 순서
            "orders": "roadaddr,addr",
            "output": "json",
        }

        try:
            # self.headers를 사용하여 생성자에서 받은 인증키 활용
            res = requests.get(REVERSE_GEOCODE_URL, headers=self.headers, params=params)

            if res.status_code != 200:
                print("Reverse Geocode Error Status:", res.status_code)
                return "주소 없음"

            data = res.json()

            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]

                region = result.get("region", {})
                land = result.get("land", {})

                # 1. 시/도, 구/군, 읍/면/동 추출
                area1 = region.get("area1", {}).get("name", "")
                area2 = region.get("area2", {}).get("name", "")
                area3 = region.get("area3", {}).get("name", "")
                area4 = region.get("area4", {}).get("name", "")  # 리/상세 단위

                # 2. 도로명/지번 정보
                road_name = land.get("name", "")
                number1 = land.get("number1", "")
                number2 = land.get("number2", "")

                # 번지/본번-부번 조합
                number = f"{number1}-{number2}" if number2 else number1

                # 3. 🔥 상세주소 파싱 (건물명 및 기타 상세 정보)
                # addition0: 건물명 (예: 63빌딩, 삼성아파트)
                # addition1: 동/층/호수 등 기타 상세 정보
                building_name = land.get("addition0", {}).get("value", "")
                detail_info = land.get("addition1", {}).get("value", "")

                # 상세주소 조립
                detail_address = " ".join(filter(None, [building_name, detail_info]))

                # 4. 전체 주소 조합
                address_components = [
                    area1,
                    area2,
                    area3,
                    area4,
                    road_name,
                    number,
                    f"({detail_address})" if detail_address else "",
                ]

                # 공백제거 및 최종 문자열 반환
                full_address = " ".join(
                    [comp for comp in address_components if comp]
                ).strip()
                return full_address if full_address else "주소 없음"

        except Exception as e:
            print("reverse_geocode error:", e)

        return "주소 없음"
