class RecommendLocation:


    def __init__(self, stores):
        self.stores = stores or []


    def find(self, recommend_categories):

        result = []


        for store in self.stores:


            category_list = [
                store.get("indsLclsNm"),
                store.get("indsMclsNm"),
                store.get("indsSclsNm")
            ]


            if any(
                category in recommend_categories
                for category in category_list
            ):

                result.append(store)


        return result