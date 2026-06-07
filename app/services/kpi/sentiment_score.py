from app.models.dataset import Dataset


class SentimentScoreKPI:
    """
    KPI #3: Sentiment Score (Индекс тональности)

    Смысл: разница между процентом позитивных и негативных отзывов.
    Значение > 0 — преобладает позитив, < 0 — негатив.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> float:
        """Возвращает Sentiment Score от -100% до +100%."""
        all_reviews = []
        for ds in datasets:
            all_reviews.extend(ds.reviews)

        positive = 0
        negative = 0

        for r in all_reviews:
            if r.rating is None:
                continue
            if r.rating >= 4:
                positive += 1
            elif r.rating <= 2:
                negative += 1

        total_with_rating = positive + negative
        if total_with_rating == 0:
            return 0.0

        score = (positive - negative) / total_with_rating * 100
        return round(score, 1)