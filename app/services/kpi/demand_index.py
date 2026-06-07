from datetime import datetime
from collections import Counter
from app.models.dataset import Dataset


class DemandIndexKPI:
    """
    KPI #8: Индекс потенциального спроса (Demand Index)

    Смысл: интегральная метрика, оценивающая рыночный спрос на основе отзывов.
    Чем больше позитивных отзывов и чем активнее растёт их поток, тем выше спрос.

    Логика:
    - 70% веса: доля позитивных отзывов
    - 30% веса: динамика роста отзывов за последние 3 месяца
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> int:
        """Возвращает Demand Index от 0 до 100."""
        all_reviews = []
        for ds in datasets:
            all_reviews.extend(ds.reviews)

        if not all_reviews:
            return 0

        # Компонент 1: Доля позитивных отзывов (70% веса)
        positive = sum(1 for r in all_reviews if r.rating is not None and r.rating >= 4)
        total_with_rating = sum(1 for r in all_reviews if r.rating is not None)

        if total_with_rating > 0:
            positive_share = positive / total_with_rating
        else:
            positive_share = 0

        # Компонент 2: Динамика роста за последние 3 месяца (30% веса)
        now = datetime.now()
        month_counter = Counter()

        for r in all_reviews:
            if r.date and len(r.date) >= 7:
                try:
                    review_date = datetime.strptime(r.date[:7], "%Y-%m")
                    months_ago = (now.year - review_date.year) * 12 + (now.month - review_date.month)
                    if months_ago <= 3:
                        month_counter[months_ago] += 1
                except ValueError:
                    continue

        # Рост = (отзывы за последний месяц) / (среднее за предыдущие 2 месяца)
        recent = month_counter.get(0, 0)
        prev_avg = (month_counter.get(1, 0) + month_counter.get(2, 0)) / 2 if any(
            month_counter.get(i, 0) > 0 for i in [1, 2]) else 0

        if prev_avg > 0:
            growth_rate = min(recent / prev_avg, 2.0)  # Ограничиваем максимум 2x
        else:
            growth_rate = 1.0 if recent > 0 else 0.5

        # Итоговый индекс
        demand_index = int((positive_share * 0.7 + growth_rate * 0.3) * 100)
        return min(max(demand_index, 0), 100)  # Ограничиваем 0-100