from app.models.dataset import Dataset
import numpy as np

class AvgSentimentKPI:
    """
    KPI #4: Средний сентимент товара

    Смысл: средний уровень удовлетворенности клиентов (аналог звездного рейтинга).
    Близко к +1 – большинство отзывов позитивны,
    близко к −1 – преобладают жалобы.
    Расчет на основе рейтинга (переводим 5-балльную шкалу в шкалу -1..+1)
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> float:
        """
        Возвращает средний сентимент от -1.0 до +1.0.

        Конвертируем рейтинг из шкалы 1-5 в шкалу -1..+1:
        рейтинг 1 -> -1.0 (очень негативно)
        рейтинг 2 -> -0.5
        рейтинг 3 -> 0.0 (нейтрально)
        рейтинг 4 -> +0.5
        рейтинг 5 -> +1.0 (очень позитивно)
        """
        ratings = []
        for ds in datasets:
            ratings.extend(ds.reviews)

        if not ratings:
            return 0.0

        # Конвертируем рейтинг в сентимент
        sentiment_scores = []
        for review in ratings:
            if review.rating is not None:
                # Преобразуем рейтинг 1-5 в диапазон -1..+1
                # Формула: (rating - 3) / 2
                # 1 -> -1, 2 -> -0.5, 3 -> 0, 4 -> 0.5, 5 -> 1
                sentiment_score = (review.rating - 3) / 2
                sentiment_scores.append(sentiment_score)

        if not sentiment_scores:
            return 0.0

        # Вычисляем среднее арифметическое
        avg_sentiment = np.mean(sentiment_scores)

        # Округляем до 2 знаков
        return round(float(avg_sentiment), 2)