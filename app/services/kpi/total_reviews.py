from app.models.dataset import Dataset


class TotalReviewsKPI:
    """
    KPI #1: Общее число отзывов (Total Reviews)

    Смысл: отражает объём обратной связи и вовлечённость клиентов.
    """

    @staticmethod
    def calculate(datasets: list[Dataset]) -> int:
        """Возвращает общее количество отзывов во всех датасетах."""
        return sum(ds.reviews_count for ds in datasets)