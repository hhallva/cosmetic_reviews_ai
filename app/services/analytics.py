from app.models.dataset import Dataset
from app.services.kpi import (
    TotalReviewsKPI,
    SentimentDistributionKPI,
    SentimentScoreKPI,
    AvgRatingKPI,
    ProblemsIndexKPI,
    BestSegmentKPI,
    WorstSegmentKPI,
    DemandIndexKPI,
)


class AnalyticsService:
    def __init__(self, datasets: list[Dataset]):
        self.datasets = datasets

    def get_full_dashboard(self) -> dict:
        """Собирает все KPI и аналитику для дашборда."""
        return {
            # KPI
            "total_reviews": TotalReviewsKPI.calculate(self.datasets),
            "sentiment_dist": SentimentDistributionKPI.calculate(self.datasets),
            "sentiment_score": SentimentScoreKPI.calculate(self.datasets),
            "avg_rating": AvgRatingKPI.calculate(self.datasets),
            "problems_index": ProblemsIndexKPI.calculate(self.datasets),
            "best_segment": BestSegmentKPI.calculate(self.datasets),
            "worst_segment": WorstSegmentKPI.calculate(self.datasets),
            "demand_index": DemandIndexKPI.calculate(self.datasets),

            # Дополнительная аналитика (топ слов, pros/cons, динамика)
            "top_pros": self._get_top_pros(),
            "top_cons": self._get_top_cons(),
            "top_words": self._get_top_words(),
            "reviews_over_time": self._get_reviews_over_time(),
        }

    def _get_top_pros(self, limit: int = 10) -> list[dict]:
        from collections import Counter
        counter = Counter()
        for ds in self.datasets:
            for r in ds.reviews:
                for p in r.pros:
                    counter[p.lower()] += 1
        return [{"text": text, "count": count} for text, count in counter.most_common(limit)]

    def _get_top_cons(self, limit: int = 10) -> list[dict]:
        from collections import Counter
        counter = Counter()
        for ds in self.datasets:
            for r in ds.reviews:
                for c in r.cons:
                    counter[c.lower()] += 1
        return [{"text": text, "count": count} for text, count in counter.most_common(limit)]

    def _get_top_words(self, limit: int = 20) -> list[dict]:
        import re
        from collections import Counter

        stop_words = {
            "и", "в", "не", "на", "я", "быть", "с", "он", "что", "а", "по", "это",
            "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
            "мы", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг",
            "ли", "если", "уже", "или", "ни", "бы", "был", "была", "были",
            "то", "тот", "эта", "этот", "эти", "все", "всё", "мне", "меня",
            "для", "от", "до", "как", "чтобы", "который", "которая", "которое",
            "очень", "более", "менее", "сам", "сама", "сами", "свой", "своя",
        }

        counter = Counter()
        for ds in self.datasets:
            for r in ds.reviews:
                words = re.findall(r"[а-яёa-z]{3,}", r.text.lower(), re.IGNORECASE)
                for w in words:
                    if w not in stop_words:
                        counter[w] += 1

        return [{"word": word, "count": count} for word, count in counter.most_common(limit)]

    def _get_reviews_over_time(self) -> list[dict]:
        from collections import Counter
        month_counter = Counter()
        for ds in self.datasets:
            for r in ds.reviews:
                if r.date and len(r.date) >= 7:
                    month = r.date[:7]
                    month_counter[month] += 1

        return sorted(
            [{"month": m, "count": c} for m, c in month_counter.items()],
            key=lambda x: x["month"],
        )