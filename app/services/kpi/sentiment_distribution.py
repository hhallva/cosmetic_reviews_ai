from app.models.dataset import Dataset


class SentimentDistributionKPI:
    """
    KPI #2: Распределение отзывов по тональности (Sentiment Distribution)

    Смысл: показывает процент позитивных, негативных и нейтральных отзывов.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> dict:
        """
        Возвращает распределение:
        {
            "positive": int,
            "neutral": int,
            "negative": int,
            "unknown": int,
            "positive_pct": float,
            "neutral_pct": float,
            "negative_pct": float
        }
        """
        all_reviews = []
        for ds in datasets:
            all_reviews.extend(ds.reviews)

        dist = {"positive": 0, "neutral": 0, "negative": 0, "unknown": 0}

        for r in all_reviews:
            if r.rating is None:
                dist["unknown"] += 1
            elif r.rating >= 4:
                dist["positive"] += 1
            elif r.rating == 3:
                dist["neutral"] += 1
            else:
                dist["negative"] += 1

        total_with_rating = dist["positive"] + dist["neutral"] + dist["negative"]

        if total_with_rating > 0:
            dist["positive_pct"] = int(round(dist["positive"] / total_with_rating * 100, 1))
            dist["neutral_pct"] = int(round(dist["neutral"] / total_with_rating * 100, 1))
            dist["negative_pct"] = int(round(dist["negative"] / total_with_rating * 100, 1))
        else:
            dist["positive_pct"] = 0
            dist["neutral_pct"] = 0
            dist["negative_pct"] = 0

        return dist