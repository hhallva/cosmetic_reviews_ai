# app/services/kpi/demand_index_kpi.py
from datetime import datetime
import numpy as np
from typing import List, Tuple
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

        # Извлекаем рейтинги и даты в NumPy массивы
        ratings = np.array([r.rating for r in all_reviews if r.rating is not None])
        dates = [r.date for r in all_reviews if r.date and len(r.date) >= 7]

        if len(ratings) == 0:
            return 0

        # Компонент 1: Доля позитивных отзывов (70% веса)
        positive_share = np.sum(ratings >= 4) / len(ratings)

        # Компонент 2: Динамика роста за последние 3 месяца (30% веса)
        growth_rate = DemandIndexKPI._calculate_growth_rate(dates)

        # Итоговый индекс
        demand_index = int((positive_share * 0.7 + growth_rate * 0.3) * 100)
        return np.clip(demand_index, 0, 100)

    @staticmethod
    def _calculate_growth_rate(dates: List[str]) -> float:
        """Рассчитывает темп роста отзывов за последние 3 месяца"""
        if not dates:
            return 0.5

        now = datetime.now()

        # Парсим даты и вычисляем возраст в месяцах
        months_ago_list = []
        for date_str in dates:
            try:
                review_date = datetime.strptime(date_str[:7], "%Y-%m")
                months_ago = (now.year - review_date.year) * 12 + (now.month - review_date.month)
                if months_ago <= 3:
                    months_ago_list.append(months_ago)
            except ValueError:
                continue

        if not months_ago_list:
            return 0.5

        # Используем NumPy для подсчета
        months_array = np.array(months_ago_list)

        # Подсчитываем отзывы по месяцам
        recent_count = np.sum(months_array == 0)
        prev_1_count = np.sum(months_array == 1)
        prev_2_count = np.sum(months_array == 2)

        prev_avg = (prev_1_count + prev_2_count) / 2 if (prev_1_count + prev_2_count) > 0 else 0

        if prev_avg > 0:
            growth_rate = min(recent_count / prev_avg, 2.0)
        else:
            growth_rate = 1.0 if recent_count > 0 else 0.5

        return growth_rate