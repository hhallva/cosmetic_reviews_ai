import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.models.dataset import Dataset, DatasetMeta
from app.services.dataset_loader import DatasetLoader


class DatasetManager:
    def __init__(self, storage_dir: str | Path = "data/datasets"):
        self.loader = DatasetLoader(storage_dir)
        self.storage_dir = Path(storage_dir)
        self.meta_file = self.storage_dir / "datasets_meta.json"

    def upload_dataset(self, file_path: str | Path, skip_duplicate: bool = True) -> DatasetMeta:
        """Загружает датасет из файла. Если skip_duplicate — проверяет дубли."""
        dataset = self.loader.load_from_file(file_path)

        if skip_duplicate:
            existing = self.list_datasets()
            for m in existing:
                if m.product == dataset.product and m.brand == dataset.brand:
                    print(f"⚠️ Датасет уже существует: [{m.id}] {m.brand} - {m.product}")
                    return m

        self.loader.save(dataset)
        self._save_meta(dataset)
        return self._to_meta(dataset)

    def list_datasets(self) -> list[DatasetMeta]:
        if not self.meta_file.exists():
            return []
        with open(self.meta_file, "r", encoding="utf-8") as f:
            metas = json.load(f)
        return [DatasetMeta(**m) for m in metas]

    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        file_path = self.storage_dir / f"{dataset_id}.json"
        if not file_path.exists():
            return None
        return self.loader.load_from_file(file_path)

    def delete_dataset(self, dataset_id: str) -> bool:
        file_path = self.storage_dir / f"{dataset_id}.json"
        if not file_path.exists():
            return False
        file_path.unlink()
        self._remove_from_meta(dataset_id)
        return True

    def get_by_period(self, from_date: str, to_date: str) -> list[DatasetMeta]:
        from_dt = datetime.fromisoformat(from_date)
        to_dt = datetime.fromisoformat(to_date)
        return [
            m for m in self.list_datasets()
            if from_dt <= datetime.fromisoformat(m.uploaded_at) <= to_dt
        ]

    def get_by_brand(self, brand: str) -> list[DatasetMeta]:
        return [m for m in self.list_datasets() if m.brand.lower() == brand.lower()]

    def get_multiple(self, dataset_ids: list[str]) -> list[Dataset]:
        datasets = []
        for ds_id in dataset_ids:
            ds = self.get_dataset(ds_id)
            if ds:
                datasets.append(ds)
        return datasets

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

    def _to_meta(self, dataset: Dataset) -> DatasetMeta:
        return DatasetMeta(
            id=dataset.id,
            source=dataset.source,
            product=dataset.product,
            brand=dataset.brand,
            uploaded_at=dataset.uploaded_at,
            reviews_count=dataset.reviews_count,
        )