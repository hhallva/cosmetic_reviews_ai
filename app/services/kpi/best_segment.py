from app.models.dataset import Dataset


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
        for ds in datasets:
            brand = ds.brand
            if brand not in brand_stats:
                brand_stats[brand] = {"ratings": [], "positive": 0, "total": 0}

            for r in ds.reviews:
                if r.rating is not None:
                    brand_stats[brand]["ratings"].append(r.rating)
                    brand_stats[brand]["total"] += 1
                    if r.rating >= 4:
                        brand_stats[brand]["positive"] += 1

        # Находим лучший бренд по среднему рейтингу
        best_brand = None
        best_avg = 0

        for brand, stats in brand_stats.items():
            if stats["ratings"]:
                avg = sum(stats["ratings"]) / len(stats["ratings"])
                if avg > best_avg:
                    best_avg = avg
                    best_brand = brand

        if not best_brand:
            return {"brand": "N/A", "product": "N/A", "avg_rating": 0, "positive_pct": 0}

        stats = brand_stats[best_brand]
        positive_pct = round(stats["positive"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0

        # Находим продукт этого бренда с наивысшим рейтингом
        best_product = None
        best_product_avg = 0

        for ds in datasets:
            if ds.brand == best_brand:
                ratings = [r.rating for r in ds.reviews if r.rating is not None]
                if ratings:
                    avg = sum(ratings) / len(ratings)
                    if avg > best_product_avg:
                        best_product_avg = avg
                        best_product = ds.product

        return {
            "brand": best_brand,
            "product": best_product or "N/A",
            "avg_rating": round(best_avg, 2),
            "positive_pct": positive_pct,
        }