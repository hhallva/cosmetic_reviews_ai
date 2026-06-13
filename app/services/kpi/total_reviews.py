# app/services/kpi/total_reviews_kpi.py
import numpy as np
from app.models.dataset import Dataset


class TotalReviewsKPI:
    """
    KPI #1: Общее число отзывов (Total Reviews)

    Смысл: отражает объём обратной связи и вовлечённость клиентов.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> int:
        """Возвращает общее количество отзывов во всех датасетах."""
        if not datasets:
            return 0

        # Собираем количество отзывов из каждого датасета в NumPy массив
        reviews_counts = np.array([ds.reviews_count for ds in datasets])

        # Суммируем с помощью NumPy
        return int(np.sum(reviews_counts))