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
        positive = 0
        negative = 0
        total_rated = 0

        for ds in datasets:
            reviews = ds.reviews or []
            for r in reviews:
                if r.rating is None:
                    continue

                total_rated += 1
                if r.rating >= 4:
                    positive += 1
                elif r.rating <= 2:
                    negative += 1

        if total_rated == 0:
            return 0.0

        score = (positive - negative) / total_rated * 100
        return round(score, 1)