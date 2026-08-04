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

            category = (
                store.get("indsMclsNm")
                or store.get("indsLclsNm")
                or "기타"
            )


            if category not in categories:
                categories[category] = []


            categories[category].append(store)



        results = []


        for category, shops in categories.items():


            count = len(shops)


            # -----------------
            # 창업 점수 계산
            # -----------------

            scarcity = max(
                0,
                40 - count * 2
            )


            competition = max(
                0,
                30 - count
            )


            score = (
                scarcity
                + competition
                + 30
            )


            if score > 100:
                score = 100



            # 대표 위치 선정
            # 중앙 위치 계산

            lat = sum(
                s["lat"]
                for s in shops
            ) / count


            lon = sum(
                s["lon"]
                for s in shops
            ) / count



            results.append(
                {
                    "업종": category,
                    "매장수": count,
                    "점수": score,
                    "추천위도": lat,
                    "추천경도": lon,
                    "추천매장": shops[0]
                }
            )


        return sorted(
            results,
            key=lambda x:x["점수"],
            reverse=True
        )