# app/services/kpi/worst_segment_kpi.py
import numpy as np
from collections import defaultdict
from app.models.dataset import Dataset


class WorstSegmentKPI:
    """
    KPI #7: Проблемный продуктный сегмент (Worst Brand/Category)

    Смысл: бренд или продукт с наивысшей долей негативных отзывов.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> dict:
        """
        Возвращает худший сегмент с использованием NumPy
        """
        if not datasets:
            return {"brand": "N/A", "product": "N/A", "avg_rating": 0, "negative_pct": 0}

        # Группируем рейтинги по брендам
        brand_ratings = defaultdict(list)
        brand_negative_counts = defaultdict(int)
        brand_total_counts = defaultdict(int)

        for ds in datasets:
            ratings = [r.rating for r in ds.reviews if r.rating is not None]
            if ratings:
                ratings_array = np.array(ratings)
                brand_ratings[ds.brand].extend(ratings)
                brand_negative_counts[ds.brand] += np.sum(ratings_array <= 2)
                brand_total_counts[ds.brand] += len(ratings)

        # Находим худший бренд по наименьшему среднему рейтингу
        worst_brand = None
        worst_avg = float('inf')
        brand_avg_dict = {}

        for brand, ratings in brand_ratings.items():
            if ratings:
                avg = np.mean(ratings)
                brand_avg_dict[brand] = avg
                if avg < worst_avg:
                    worst_avg = avg
                    worst_brand = brand

        if not worst_brand:
            return {"brand": "N/A", "product": "N/A", "avg_rating": 0, "negative_pct": 0}

        # Вычисляем процент негативных отзывов для худшего бренда
        total_reviews = brand_total_counts[worst_brand]
        negative_pct = round(brand_negative_counts[worst_brand] / total_reviews * 100, 1) if total_reviews > 0 else 0

        # Находим худший продукт внутри бренда
        worst_product = WorstSegmentKPI._find_worst_product(datasets, worst_brand)

        return {
            "brand": worst_brand,
            "product": worst_product,
            "avg_rating": round(float(worst_avg), 2),
            "negative_pct": negative_pct,
        }

    @staticmethod
    def _find_worst_product(datasets: list[Dataset], brand: str) -> str:
        """Находит худший продукт указанного бренда"""
        worst_product = "N/A"
        worst_avg = float('inf')

        for ds in datasets:
            if ds.brand == brand:
                ratings = [r.rating for r in ds.reviews if r.rating is not None]
                if ratings:
                    avg = np.mean(ratings)
                    if avg < worst_avg:
                        worst_avg = avg
                        worst_product = ds.product

        return worst_product