from app.models.dataset import Dataset


class WorstSegmentKPI:
    """
    KPI #7: Проблемный продуктный сегмент (Worst Brand/Category)

    Смысл: бренд или продукт с наивысшей долей негативных отзывов.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> dict:
        """
        Возвращает худший сегмент:
        {
            "brand": str,
            "product": str,
            "avg_rating": float,
            "negative_pct": float
        }
        """
        if not datasets:
            return {"brand": "N/A", "product": "N/A", "avg_rating": 0, "negative_pct": 0}

        # Группируем по бренду
        brand_stats = {}
        for ds in datasets:
            brand = ds.brand
            if brand not in brand_stats:
                brand_stats[brand] = {"ratings": [], "negative": 0, "total": 0}

            for r in ds.reviews:
                if r.rating is not None:
                    brand_stats[brand]["ratings"].append(r.rating)
                    brand_stats[brand]["total"] += 1
                    if r.rating <= 2:
                        brand_stats[brand]["negative"] += 1

        # Находим худший бренд по наименьшему среднему рейтингу
        worst_brand = None
        worst_avg = float('inf')

        for brand, stats in brand_stats.items():
            if stats["ratings"]:
                avg = sum(stats["ratings"]) / len(stats["ratings"])
                if avg < worst_avg:
                    worst_avg = avg
                    worst_brand = brand

        if not worst_brand:
            return {"brand": "N/A", "product": "N/A", "avg_rating": 0, "negative_pct": 0}

        stats = brand_stats[worst_brand]
        negative_pct = round(stats["negative"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0

        # Находим продукт этого бренда с наименьшим рейтингом
        worst_product = None
        worst_product_avg = float('inf')

        for ds in datasets:
            if ds.brand == worst_brand:
                ratings = [r.rating for r in ds.reviews if r.rating is not None]
                if ratings:
                    avg = sum(ratings) / len(ratings)
                    if avg < worst_product_avg:
                        worst_product_avg = avg
                        worst_product = ds.product

        return {
            "brand": worst_brand,
            "product": worst_product or "N/A",
            "avg_rating": round(worst_avg, 2),
            "negative_pct": negative_pct,
        }