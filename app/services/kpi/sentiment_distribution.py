# app/services/kpi/sentiment_distribution_kpi.py
import numpy as np
from app.models.dataset import Dataset


class SentimentDistributionKPI:
    """
    KPI #2: Распределение отзывов по тональности (Sentiment Distribution)

    Смысл: показывает процент позитивных, негативных и нейтральных отзывов.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> dict:
        """
        Возвращает распределение с использованием NumPy
        """
        all_reviews = []
        for ds in datasets:
            all_reviews.extend(ds.reviews)

        if not all_reviews:
            return SentimentDistributionKPI._empty_distribution()

        # Извлекаем рейтинги в NumPy массив
        ratings = np.array([r.rating for r in all_reviews])

        # Считаем распределение с помощью NumPy
        positive_count = np.sum((ratings >= 4) & (ratings <= 5))
        neutral_count = np.sum(ratings == 3)
        negative_count = np.sum((ratings >= 1) & (ratings <= 2))
        unknown_count = np.sum(np.isnan(ratings.astype(float))) if ratings.dtype == float else 0

        # Для целочисленных рейтингов unknown считаем отдельно
        if unknown_count == 0:
            unknown_count = np.sum(ratings == None) if hasattr(ratings, '__contains__') else 0

        total_with_rating = positive_count + neutral_count + negative_count

        if total_with_rating > 0:
            positive_pct = round(positive_count / total_with_rating * 100, 1)
            neutral_pct = round(neutral_count / total_with_rating * 100, 1)
            negative_pct = round(negative_count / total_with_rating * 100, 1)
        else:
            positive_pct = neutral_pct = negative_pct = 0

        return {
            "positive": int(positive_count),
            "neutral": int(neutral_count),
            "negative": int(negative_count),
            "unknown": int(unknown_count),
            "positive_pct": positive_pct,
            "neutral_pct": neutral_pct,
            "negative_pct": negative_pct,
        }

    @staticmethod
    def _empty_distribution() -> dict:
        """Возвращает пустое распределение"""
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "unknown": 0,
            "positive_pct": 0,
            "neutral_pct": 0,
            "negative_pct": 0,
        }