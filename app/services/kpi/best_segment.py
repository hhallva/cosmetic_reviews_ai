from collections import defaultdict

from app.models.dataset import Dataset
import numpy as np

class BestSegmentKPI:
    """
    KPI #6: Лучший продуктный сегмент (Best Brand/Category)

    Смысл: бренд или продукт с наивысшим уровнем удовлетворённости.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> dict:
        """
        Возвращает лучший сегмент:
        {
            "brand": str,
            "product": str,
            "avg_rating": float,
            "positive_pct": float
        }
        """
        if not datasets:
            return {"brand": "N/A", "product": "N/A", "avg_rating": 0, "positive_pct": 0}

        # Группируем по бренду
        brand_stats = {}

        brand_ratings = defaultdict(list)
        brand_positive_counts = defaultdict(int)
        brand_total_counts = defaultdict(int)

        for ds in datasets:
            ratings = [r.rating for r in ds.reviews if r.rating is not None]
            if ratings:
                # NumPy массив для этого датасета
                ratings_array = np.array(ratings)
                brand_ratings[ds.brand].extend(ratings)
                brand_positive_counts[ds.brand] += np.sum(ratings_array >= 4)
                brand_total_counts[ds.brand] += len(ratings)

        best_brand = None
        best_avg = 0
        brand_avg_dict = {}

        for brand, ratings in brand_ratings.items():
            if ratings:
                avg = np.mean(ratings)
                brand_avg_dict[brand] = avg
                if avg > best_avg:
                    best_avg = avg
                    best_brand = brand

        if not best_brand:
            return {"brand": "N/A", "product": "N/A", "avg_rating": 0, "positive_pct": 0}

        total_reviews = brand_total_counts[best_brand]
        positive_pct = round(brand_positive_counts[best_brand] / total_reviews * 100, 1) if total_reviews > 0 else 0

        best_product = BestSegmentKPI._find_best_product(datasets, best_brand)

        return {
            "brand": best_brand,
            "product": best_product,
            "avg_rating": round(best_avg, 2),
            "positive_pct": positive_pct,
        }

    @staticmethod
    def _find_best_product(datasets: list[Dataset], brand: str) -> str:
        """Находит лучший продукт указанного бренда"""
        best_product = "N/A"
        best_avg = 0

        for ds in datasets:
            if ds.brand == brand:
                ratings = [r.rating for r in ds.reviews if r.rating is not None]
                if ratings:
                    avg = np.mean(ratings)
                    if avg > best_avg:
                        best_avg = avg
                        best_product = ds.product

        return best_product