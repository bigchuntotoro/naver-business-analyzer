from collections import Counter


class StartupLocation:

    def __init__(self, stores):
        self.stores = stores or []

    def analyze(self):
        if not self.stores:
            return []

        categories = {}

        # 업종별 매장 그룹화
        for store in self.stores:
            category = store.get("indsMclsNm") or store.get("indsLclsNm") or "기타"

            if category not in categories:
                categories[category] = []

            categories[category].append(store)

        results = []

        for category, shops in categories.items():
            count = len(shops)

            # -----------------
            # 창업 점수 계산
            # -----------------
            scarcity = max(0, 40 - count * 2)
            competition = max(0, 30 - count)
            score = scarcity + competition + 30

            if score > 100:
                score = 100

            # 대표 위치 선정 (중앙 위치 계산)
            lat = sum(float(s.get("lat", 0)) for s in shops) / count
            lon = sum(float(s.get("lon", 0)) for s in shops) / count

            # 대표 매장
            representative_shop = shops[0]

            results.append(
                {
                    "업종": category,
                    "매장수": count,
                    "점수": score,
                    "추천위도": lat,
                    "추천경도": lon,
                    "lat": lat,  # 🔥 메인 앱 파싱용 Key 추가
                    "lng": lon,  # 🔥 메인 앱 파싱용 Key 추가
                    "추천매장": representative_shop,
                }
            )

        return sorted(results, key=lambda x: x["점수"], reverse=True)
