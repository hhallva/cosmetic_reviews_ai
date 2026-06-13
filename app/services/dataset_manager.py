import json
from pathlib import Path
from typing import Optional

from app.models.dataset import Dataset, DatasetMeta, BrandStats, ProductStats
from app.services.dataset_loader import DatasetLoader


class DatasetManager:
    def __init__(self, storage_dir: str | Path = "data/datasets"):
        self.loader = DatasetLoader(storage_dir)
        self.storage_dir = Path(storage_dir)
        self.meta_file = self.storage_dir / "datasets_meta.json"

    def upload_dataset(self,
        reviews_file: str | Path,
        brand: str,
        category: str,
        product: str,
        source: str = "unknown",
    ) -> DatasetMeta:
        """Загружает датасет: принимает файл с отзывами + метаданные."""
        reviews = self.loader.load_reviews_from_file(reviews_file)

        dataset = Dataset(
            brand=brand,
            category=category,
            product=product,
            source=source,
            reviews=reviews,
        )

        self.loader.save_dataset(dataset)
        self._save_meta(dataset)
        return self._to_meta(dataset)


    def list_datasets(self) -> list[DatasetMeta]:
        """Все датасеты."""
        if not self.meta_file.exists():
            return []
        with open(self.meta_file, "r", encoding="utf-8") as f:
            metas = json.load(f)
        return [DatasetMeta(**m) for m in metas]

    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Получить датасет по ID."""
        file_path = self.storage_dir / f"{dataset_id}.json"
        if not file_path.exists():
            return None
        return self.loader.load_dataset(file_path)

    def delete_dataset(self, dataset_id: str) -> bool:
        """Удалить датасет."""
        file_path = self.storage_dir / f"{dataset_id}.json"
        if not file_path.exists():
            return False
        file_path.unlink()
        self._remove_from_meta(dataset_id)
        return True

    def get_datasets_by_product(self, brand: str, product: str) -> list[DatasetMeta]:
        """Все датасеты для конкретного продукта."""
        return [
            m for m in self.list_datasets()
            if m.brand.lower() == brand.lower() and m.product.lower() == product.lower()
        ]

    def get_datasets_by_brand(self, brand: str) -> list[DatasetMeta]:
        """Все датасеты бренда."""
        return [m for m in self.list_datasets() if m.brand.lower() == brand.lower()]

    def get_brands(self) -> list[BrandStats]:
        """Статистика по всем брендам."""
        datasets = self.list_datasets()
        brands = {}

        for ds in datasets:
            if ds.brand not in brands:
                brands[ds.brand] = {
                    "datasets": set(),
                    "categories": set(),
                    "products": set(),
                    "reviews": 0,
                }
            brands[ds.brand]["datasets"].add(ds.id)
            brands[ds.brand]["categories"].add(ds.category)
            brands[ds.brand]["products"].add(ds.product)
            brands[ds.brand]["reviews"] += ds.reviews_count

        return [
            BrandStats(
                brand=brand,
                datasets_count=len(data["datasets"]),
                categories_count=len(data["categories"]),
                products_count=len(data["products"]),
                reviews_count=data["reviews"],
            )
            for brand, data in brands.items()
        ]

    def get_products_by_brand(self, brand: str) -> list[ProductStats]:
        """Статистика по продуктам бренда."""
        datasets = self.get_datasets_by_brand(brand)
        products = {}

        for ds in datasets:
            key = ds.product
            if key not in products:
                products[key] = {
                    "category": ds.category,
                    "datasets": set(),
                    "reviews": 0,
                    "ratings": [],
                }
            products[key]["datasets"].add(ds.id)
            products[key]["reviews"] += ds.reviews_count

            # Загружаем полный датасет для рейтинга
            full_ds = self.get_dataset(ds.id)
            if full_ds:
                for r in full_ds.reviews:
                    if r.rating is not None:
                        products[key]["ratings"].append(r.rating)

        result = []
        for product, data in products.items():
            if data["ratings"]:
                ratings_sum = float(sum(data["ratings"]))  # Convert to float
                ratings_len = len(data["ratings"])
                avg_rating = round(ratings_sum / ratings_len, 2)
            else:
                avg_rating = 0
            result.append(
                ProductStats(
                    product=product,
                    category=data["category"],
                    datasets_count=len(data["datasets"]),
                    reviews_count=data["reviews"],
                    avg_rating=avg_rating,
                )
            )

        return result

    def get_categories(self, brand: str) -> list[str]:
        """Все категории бренда."""
        datasets = self.get_datasets_by_brand(brand)
        return sorted(set(ds.category for ds in datasets))

    def _save_meta(self, dataset: Dataset):
        metas = self.list_datasets()
        metas = [m for m in metas if m.id != dataset.id]
        metas.append(self._to_meta(dataset))
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump([m.model_dump() for m in metas], f, ensure_ascii=False, indent=2)

    def _remove_from_meta(self, dataset_id: str):
        metas = [m for m in self.list_datasets() if m.id != dataset_id]
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump([m.model_dump() for m in metas], f, ensure_ascii=False, indent=2)
    @staticmethod
    def _to_meta(dataset: Dataset) -> DatasetMeta:
        return DatasetMeta(
            id=dataset.id,
            brand=dataset.brand,
            category=dataset.category,
            product=dataset.product,
            source=dataset.source,
            uploaded_at=dataset.uploaded_at,
            reviews_count=dataset.reviews_count,
        )