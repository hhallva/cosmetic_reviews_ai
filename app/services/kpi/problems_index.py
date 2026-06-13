# app/services/kpi/problems_index_kpi.py
import numpy as np
from app.models.dataset import Dataset


class ProblemsIndexKPI:
    """
    KPI #5: Показатель жалоб (Problems Index или TGW)

    Смысл: среднее число упомянутых проблем (cons) в отзывах.
    Чем выше значение, тем больше жалоб содержит каждый отзыв.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> float:
        all_reviews = []
        for ds in datasets:
            all_reviews.extend(ds.reviews)

        if not all_reviews:
            return 0.0

        # Используем NumPy для быстрого подсчета
        problems_counts = np.array([len(r.cons) for r in all_reviews])
        avg_problems = np.mean(problems_counts)

        return round(float(avg_problems), 2)