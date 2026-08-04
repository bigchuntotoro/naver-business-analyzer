from collections import Counter

class CommercialAnalyzer:
    def __init__(self, stores):
        self.stores = stores or []

    def analyze(self):
        if not self.stores:
            return {
                "total": 0,
                "categories": {},
                "score": 0
            }

        # 업종 카운트
        categories = [store.get("indsLclsNm", "기타") for store in self.stores]
        counter = Counter(categories)

        total = len(self.stores)

        # 경쟁도 계산 (간단 버전)
        competition_score = total

        # 다양성 점수
        diversity_score = len(counter)

        # 최종 점수 (튜닝 가능)
        score = (diversity_score * 2) - competition_score * 0.5

        return {
            "total": total,
            "categories": dict(counter),
            "score": round(score, 2)
        }