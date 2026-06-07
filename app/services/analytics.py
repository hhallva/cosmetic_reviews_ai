import re
from collections import Counter

from app.models.dataset import Dataset


class AnalyticsService:
    def __init__(self, datasets: list[Dataset]):
        self.datasets = datasets
        self.all_reviews = []
        for ds in datasets:
            self.all_reviews.extend(ds.reviews)

    def get_summary(self) -> dict:
        total = len(self.all_reviews)
        ratings = [r.rating for r in self.all_reviews if r.rating is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0

        rating_dist = Counter(ratings)
        rating_distribution = {i: rating_dist.get(i, 0) for i in range(1, 6)}

        return {
            "total_reviews": total,
            "avg_rating": avg_rating,
            "rating_distribution": rating_distribution,
            "datasets_count": len(self.datasets),
        }

    def get_top_pros(self, limit: int = 10) -> list[dict]:
        counter = Counter()
        for r in self.all_reviews:
            for p in r.pros:
                counter[p.lower()] += 1
        return [{"text": text, "count": count} for text, count in counter.most_common(limit)]

    def get_top_cons(self, limit: int = 10) -> list[dict]:
        counter = Counter()
        for r in self.all_reviews:
            for c in r.cons:
                counter[c.lower()] += 1
        return [{"text": text, "count": count} for text, count in counter.most_common(limit)]

    def get_top_words(self, limit: int = 20) -> list[dict]:
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
        for r in self.all_reviews:
            words = re.findall(r"[а-яёa-z]{3,}", r.text.lower(), re.IGNORECASE)
            for w in words:
                if w not in stop_words:
                    counter[w] += 1

        return [{"word": word, "count": count} for word, count in counter.most_common(limit)]

    def get_reviews_over_time(self) -> list[dict]:
        month_counter = Counter()
        for r in self.all_reviews:
            if r.date and len(r.date) >= 7:
                month = r.date[:7]
                month_counter[month] += 1

        return sorted(
            [{"month": m, "count": c} for m, c in month_counter.items()],
            key=lambda x: x["month"],
        )

    def get_sentiment_distribution(self) -> dict:
        dist = {"positive": 0, "neutral": 0, "negative": 0, "unknown": 0}
        for r in self.all_reviews:
            if r.rating is None:
                dist["unknown"] += 1
            elif r.rating >= 4:
                dist["positive"] += 1
            elif r.rating == 3:
                dist["neutral"] += 1
            else:
                dist["negative"] += 1
        return dist

    def get_full_dashboard(self) -> dict:
        return {
            "summary": self.get_summary(),
            "sentiment": self.get_sentiment_distribution(),
            "top_pros": self.get_top_pros(),
            "top_cons": self.get_top_cons(),
            "top_words": self.get_top_words(),
            "reviews_over_time": self.get_reviews_over_time(),
        }