import json
from pathlib import Path

from app.models.dataset import Dataset, Review

class DatasetLoadError(Exception):
    pass

class DatasetLoader:
    """
    Принимает ВХОДНОЙ формат: просто массив отзывов
    [
        {"review_id": 1, "author": "...", "date": "...", ...},
        ...
    ]

    Сохраняет в формат с метаданными:
    {
        "id": "...",
        "brand": "...",
        "category": "...",
        "product": "...",
        "source": "...",
        "uploaded_at": "...",
        "reviews": [...]
    }
    """

    REQUIRED_KEYS = {"source", "product", "brand", "reviews"}

    def __init__(self, storage_dir: str | Path = "data/datasets"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def load_reviews_from_file(self, file_path: str | Path) -> list[Review]:
        """Загружает массив отзывов из JSON-файла."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise DatasetLoadError(f"Файл не найден: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ожидаем массив отзывов
        if not isinstance(data, list):
            raise DatasetLoadError("Ожидался массив отзывов (list)")

        return self._parse_reviews(data)

    def save_dataset(self, dataset: Dataset) -> Path:
        """Сохраняет датасет с метаданными."""
        file_path = self.storage_dir / f"{dataset.id}.json"

        data = {
            "id": dataset.id,
            "brand": dataset.brand,
            "category": dataset.category,
            "product": dataset.product,
            "source": dataset.source,
            "uploaded_at": dataset.uploaded_at,
            "reviews": [r.model_dump() for r in dataset.reviews],
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return file_path

    def load_dataset(self, file_path: str | Path) -> Dataset:
        """Загружает сохранённый датасет (с метаданными)."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise DatasetLoadError(f"Файл не найден: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Валидация метаданных
        required = {"id", "brand", "category", "product", "reviews"}
        missing = required - set(data.keys())
        if missing:
            raise DatasetLoadError(f"Отсутствуют ключи: {missing}")

        reviews = self._parse_reviews(data["reviews"])

        return Dataset(
            id=data["id"],
            brand=data["brand"],
            category=data["category"],
            product=data["product"],
            source=data.get("source", "unknown"),
            uploaded_at=data.get("uploaded_at", ""),
            reviews=reviews,
        )

    @staticmethod
    def _parse_reviews(reviews_data: list) -> list[Review]:
        """Парсит массив отзывов."""
        reviews = []
        for i, rev_data in enumerate(reviews_data, start=1):
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

        return reviews