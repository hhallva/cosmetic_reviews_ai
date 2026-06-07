import json
from pathlib import Path

from app.models.dataset import Dataset, Review


class DatasetLoadError(Exception):
    pass


class DatasetLoader:
    """
    Работает ТОЛЬКО с единым форматом:
    {
        "source": "irecommend.ru",
        "product": "Название продукта",
        "brand": "Бренд",
        "reviews": [...]
    }
    """

    REQUIRED_KEYS = {"source", "product", "brand", "reviews"}

    def __init__(self, storage_dir: str | Path = "data/datasets"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def load_from_file(self, file_path: str | Path) -> Dataset:
        file_path = Path(file_path)
        if not file_path.exists():
            raise DatasetLoadError(f"Файл не найден: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self._build(data)

    def load_from_dict(self, data: dict) -> Dataset:
        return self._build(data)

    def save(self, dataset: Dataset) -> Path:
        """Сохраняет в ТОМ ЖЕ формате, что и принимает."""
        file_path = self.storage_dir / f"{dataset.id}.json"

        data = {
            "source": dataset.source,
            "product": dataset.product,
            "brand": dataset.brand,
            "reviews": [r.model_dump() for r in dataset.reviews],
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return file_path

    def _build(self, data: dict) -> Dataset:
        # Валидация ключей
        missing = self.REQUIRED_KEYS - set(data.keys())
        if missing:
            raise DatasetLoadError(f"Отсутствуют ключи: {missing}")

        # Парсинг отзывов
        reviews = []
        for i, rev_data in enumerate(data["reviews"], start=1):
            try:
                rev = Review(
                    review_id=rev_data.get("review_id", i),
                    author=rev_data.get("author", "Unknown"),
                    date=rev_data.get("date", ""),
                    title=rev_data.get("title", ""),
                    rating=rev_data.get("rating"),
                    text=rev_data.get("text", ""),
                    pros=rev_data.get("pros", []),
                    cons=rev_data.get("cons", []),
                )
                reviews.append(rev)
            except Exception as e:
                print(f"⚠️ Пропущен отзыв #{i}: {e}")
                continue

        if not reviews:
            raise DatasetLoadError("В датасете нет валидных отзывов")

        return Dataset(
            source=str(data["source"]),
            product=str(data["product"]),
            brand=str(data["brand"]),
            reviews=reviews,
        )