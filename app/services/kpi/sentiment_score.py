# app/services/kpi/sentiment_score_kpi.py
import numpy as np
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
        # Собираем все рейтинги в NumPy массив
        ratings = []
        for ds in datasets:
            for r in ds.reviews:
                if r.rating is not None:
                    ratings.append(r.rating)

        if not ratings:
            return 0.0

        ratings_array = np.array(ratings)

        # Векторизованный подсчет
        positive = np.sum(ratings_array >= 4)
        negative = np.sum(ratings_array <= 2)
        total_rated = len(ratings_array)

        # Расчет скора
        score = (positive - negative) / total_rated * 100

        return round(float(score), 1)