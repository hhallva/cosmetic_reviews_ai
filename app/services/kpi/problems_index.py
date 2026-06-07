from app.models.dataset import Dataset


class ProblemsIndexKPI:
    """
    KPI #5: Показатель жалоб (Problems Index или TGW)

    Смысл: среднее число упомянутых проблем (cons) в отзывах.
    Чем выше значение, тем больше жалоб содержит каждый отзыв.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> float:
        """Возвращает среднее количество недостатков на отзыв."""
        all_reviews = []
        for ds in datasets:
            all_reviews.extend(ds.reviews)

        if not all_reviews:
            return 0.0

        total_problems = sum(len(r.cons) for r in all_reviews)
        return round(total_problems / len(all_reviews), 2)