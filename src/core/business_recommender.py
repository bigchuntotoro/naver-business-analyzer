from collections import Counter


class BusinessRecommender:

    def __init__(self, stores):
        self.stores = stores or []


    def recommend(self):

        if not self.stores:
            return {
                "recommend": [],
                "avoid": [],
                "reason": "데이터 부족"
            }


        categories = []

        for store in self.stores:

            category = (
                store.get("indsMclsNm")
                or store.get("indsLclsNm")
                or "기타"
            )

            categories.append(category)


        counter = Counter(categories)


        # 경쟁이 적은 업종
        recommend = sorted(
            counter.items(),
            key=lambda x: x[1]
        )[:5]


        # 경쟁이 많은 업종
        avoid = sorted(
            counter.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]


        return {
            "recommend": recommend,
            "avoid": avoid,
            "reason": "주변 업종 개수와 경쟁도를 기반으로 창업 추천"
        }