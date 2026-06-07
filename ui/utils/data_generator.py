import random
import pandas as pd
from datetime import datetime, timedelta


def generate_mock_data(product_name: str):
    total = random.randint(150, 1200)
    pos = random.randint(60, 80)
    neg = random.randint(10, 25)

    metrics = {
        "total_reviews": total, "sentiment_score": pos - neg, "pos_pct": pos,
        "neg_pct": neg, "avg_rating": round(random.uniform(3.8, 4.7), 1),
        "problems_index": round(random.uniform(0.1, 0.4), 2), "demand_index": round(random.uniform(65, 95), 1)
    }

    segments = pd.DataFrame({
        "Линейка": ["Cabaret", "Cinecitta", "Makeup Revolution", "Garden", "Rare"],
        "Sentiment Score": [75, 60, 45, 30, -15],
        "Цвет": ["#28a745", "#28a745", "#ffc107", "#ffc107", "#dc3545"]
    })

    dates = [(datetime.now() - timedelta(days=30 * i)).strftime("%b %Y") for i in range(5, -1, -1)]
    trends = pd.DataFrame({
        "Месяц": dates,
        "Позитивные": [random.randint(20, 50) + i * 5 for i in range(6)],
        "Негативные": [random.randint(5, 15) - i for i in range(6)]
    })

    sources = [
        {"name": "Wildberries", "url": "https://www.wildberries.ru", "count": random.randint(500, 2000)},
        {"name": "Ozon", "url": "https://www.ozon.ru", "count": random.randint(300, 1500)},
        {"name": "IRecommend", "url": "https://irecommend.ru", "count": random.randint(100, 800)},
    ]

    reviews = [
        {"author": "Анна К.", "rating": 5, "date": "12.05.2024", "text": "Лучшая тушь! Не осыпается весь день."},
        {"author": "Мария В.", "rating": 4, "date": "10.05.2024",
         "text": "Хорошая, но кисточка могла бы быть удобнее."},
        {"author": "Елена С.", "rating": 2, "date": "08.05.2024", "text": "Разочарована. Осыпалась через 3 часа."},
    ]

    ai_insights = f"""
    • **Общий тренд**: Продукт "{product_name}" демонстрирует устойчивый рост. Sentiment Score в зеленой зоне ({metrics['sentiment_score']}%).
    • **Зона риска**: Выявлен рост упоминаний проблемы "осыпание" в последних 15% отзывов.
    • **Рекомендация**: Индекс спроса ({metrics['demand_index']}/100) указывает на высокий потенциал. Рекомендуется усилить маркетинговую поддержку.
    """
    return metrics, segments, trends, sources, reviews, ai_insights


# Моковые сохраненные отчеты для списка
# НОВАЯ СТРУКТУРА: список словарей с отдельными полями для удобной фильтрации
MOCK_SAVED_REPORTS = [
    {
        "product": "Тушь Cabaret Premiere",
        "date": datetime(2024, 6, 1),
        "display_name": "Тушь Cabaret Premiere (от 01.06.2024)",
        "rating": 4.7,
        "reviews_count": 1243
    },
    {
        "product": "Карандаш для глаз Cinecitta",
        "date": datetime(2024, 5, 28),
        "display_name": "Карандаш для глаз Cinecitta (от 28.05.2024)",
        "rating": 4.3,
        "reviews_count": 567
    },
    {
        "product": "Помада Matte Lasting",
        "date": datetime(2024, 5, 15),
        "display_name": "Помада Matte Lasting (от 15.05.2024)",
        "rating": 4.5,
        "reviews_count": 892
    },
    {
        "product": "Тушь Cabaret Volume",
        "date": datetime(2024, 4, 20),
        "display_name": "Тушь Cabaret Volume (от 20.04.2024)",
        "rating": 4.2,
        "reviews_count": 734
    },
    {
        "product": "Тональный крем Skin Perfect",
        "date": datetime(2024, 4, 5),
        "display_name": "Тональный крем Skin Perfect (от 05.04.2024)",
        "rating": 3.9,
        "reviews_count": 445
    },
]