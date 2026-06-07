from app.models.dataset import Dataset


class AvgRatingKPI:
    """
    KPI #4: Средний рейтинг товара

    Смысл: средний уровень удовлетворённости клиентов (аналог звёздного рейтинга).
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> float:
        """Возвращает средний рейтинг от 1.0 до 5.0."""
        all_reviews = []
        for ds in datasets:
            all_reviews.extend(ds.reviews)

        ratings = [r.rating for r in all_reviews if r.rating is not None]

        if not ratings:
            return 0.0

        return round(sum(ratings) / len(ratings), 2)