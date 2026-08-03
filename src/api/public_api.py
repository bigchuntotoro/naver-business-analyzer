import requests
from config.settings import PUBLIC_DATA_KEY


STORE_URL = (
    "https://apis.data.go.kr/"
    "B553077/api/open/sdsc2/storeListInRadius"
)


class PublicStoreAPI:

    def __init__(self):
        self.key = PUBLIC_DATA_KEY


    def get_stores(
        self,
        latitude,
        longitude,
        radius=500,
        page=1,
        size=100
    ):

        params = {
            "serviceKey": self.key,
            "pageNo": page,
            "numOfRows": size,
            "radius": radius,
            "cx": longitude,  # 경도
            "cy": latitude,   # 위도
            "type": "json"
        }

        response = requests.get(
            STORE_URL,
            params=params
        )

        print("STATUS:", response.status_code)
        print(response.text[:300])

        if response.status_code != 200:
            return []

        data = response.json()

        body = data.get("body", {})
        items = body.get("items")

        # ✅ 안정 처리
        if isinstance(items, dict):
            return items.get("item", [])

        elif isinstance(items, list):
            return items

        else:
            return []