import json
from pathlib import Path
from typing import Optional

from app.models.dataset import Dataset, DatasetInfo, Product, Review


class DatasetLoadError(Exception):
    pass


class DatasetLoader:
    """Загружает JSON-датасет, валидирует и возвращает объект Dataset."""

    REQUIRED_TOP_KEYS = {"dataset_info", "product", "reviews"}
    REQUIRED_PRODUCT_KEYS = {"name", "brand"}

    def __init__(self, storage_dir: str | Path = "data/datasets"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def load_from_file(self, file_path: str | Path) -> Dataset:
        """Загружает датасет из JSON-файла."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise DatasetLoadError(f"Файл не найден: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self._validate_and_build(data, source_file=file_path.name)

    def load_from_dict(self, data: dict, source_file: str = "manual") -> Dataset:
        """Загружает датасет из dict (например, из API)."""
        return self._validate_and_build(data, source_file=source_file)

    def save(self, dataset: Dataset) -> Path:
        """Сохраняет датасет в JSON-файл."""
        file_path = self.storage_dir / f"{dataset.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dataset.model_dump(), f, ensure_ascii=False, indent=2)
        dataset.file_path = str(file_path)
        return file_path

    def _validate_and_build(self, data: dict, source_file: str) -> Dataset:
        """Валидирует структуру и собирает Dataset."""
        # Проверка топ-уровня
        missing = self.REQUIRED_TOP_KEYS - set(data.keys())
        if missing:
            raise DatasetLoadError(f"Отсутствуют ключи: {missing}")

        # Проверка product
        product_data = data["product"]
        missing_prod = self.REQUIRED_PRODUCT_KEYS - set(product_data.keys())
        if missing_prod:
            raise DatasetLoadError(f"В product отсутствуют ключи: {missing_prod}")

        # Парсинг reviews
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
                raise DatasetLoadError(f"Ошибка в отзыве #{i}: {e}")

        dataset = Dataset(
            name=source_file,
            source=data["dataset_info"].get("source", "unknown"),
            product_name=product_data["name"],
            brand=product_data["brand"],
            reviews_count=len(reviews),
            reviews=reviews,
        )

        return dataset