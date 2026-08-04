from collections import Counter


class BusinessScore:

    def __init__(self, stores):
        self.stores = stores or []

    def calculate(self):

        if not self.stores:
            return []

        categories = []

        for store in self.stores:

            category = store.get("indsMclsNm") or store.get("indsLclsNm") or "기타"

            categories.append(category)

        counter = Counter(categories)

        total = len(categories)

        results = []

        for category, count in counter.items():

            # -------------------------
            # 1. 희소성 점수 (40점)
            # 적을수록 높은 점수
            # -------------------------

            scarcity = max(0, 40 - (count * 2))

            # -------------------------
            # 2. 경쟁 점수 (30점)
            # 많을수록 감점
            # -------------------------

            competition = max(0, 30 - count)

            # -------------------------
            # 3. 다양성 점수 (20점)
            # -------------------------

            diversity = min(20, len(counter) * 2)

            # -------------------------
            # 4. 보정 점수
            # -------------------------

            bonus = 10

            score = scarcity + competition + diversity + bonus

            if score > 100:
                score = 100

            results.append({"업종": category, "매장수": count, "점수": score})

        return sorted(results, key=lambda x: x["점수"], reverse=True)
