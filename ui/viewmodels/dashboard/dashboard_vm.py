# app/viewmodels/dashboard_vm.py
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.dataset import Dataset
from app.services.analytics import AnalyticsService
from app.services.dataset_manager import DatasetManager

DATASETS_DIR = Path("data/datasets")


@dataclass
class DashboardViewModel:
    brand: str
    product: str
    manager: DatasetManager = field(default_factory=lambda: DatasetManager(DATASETS_DIR))
    selected_dataset_ids: list[str] = field(default_factory=list)
    date_from: object = None
    date_to: object = None

    @property
    def dashboard_tab(self):
        return st.session_state.get("dashboard_tab", "Дашборд")

    @staticmethod
    def set_tab(tab_name: str):
        st.session_state.dashboard_tab = tab_name

    def __post_init__(self):
        self.refresh_meta()
        if not self.selected_dataset_ids:
            self.selected_dataset_ids = [ds.id for ds in self.datasets_meta]

    def refresh_meta(self):
        self.datasets_meta = self.manager.get_datasets_by_product(self.brand, self.product)
        self.available_min_date, self.available_max_date = self._get_date_bounds()

    def _get_date_bounds(self):
        all_dates = []
        for ds_meta in self.datasets_meta:
            ds = self.manager.get_dataset(ds_meta.id)
            if not ds:
                continue
            for r in ds.reviews:
                if not r.date:
                    continue
                try:
                    all_dates.append(datetime.strptime(r.date, "%Y-%m-%d").date())
                except ValueError:
                    continue
        if not all_dates:
            return None, None
        return min(all_dates), max(all_dates)

    def get_available_datasets(self):
        return self.datasets_meta

    def set_selected_datasets(self, ids: list[str]):
        self.selected_dataset_ids = ids

    def set_dates(self, date_from: date | None, date_to: date | None):
        self.date_from = date_from
        self.date_to = date_to

    def delete_dataset(self, ds_id: str):
        self.manager.delete_dataset(ds_id)
        self.refresh_meta()
        self.selected_dataset_ids = [i for i in self.selected_dataset_ids if i != ds_id]

    def get_datasets_grouped_by_source(self):
        grouped = defaultdict(list)
        for ds_meta in self.datasets_meta:
            grouped[ds_meta.source].append(ds_meta)
        return dict(grouped)

    def get_datasets(self):
        return self.datasets_meta

    def get_selected_datasets(self):
        datasets = []
        for ds_id in self.selected_dataset_ids:
            ds = self.manager.get_dataset(ds_id)
            if ds:
                datasets.append(ds)
        return datasets

    def apply_date_filter(self, datasets: list[Dataset]):
        if not self.date_from and not self.date_to:
            return datasets

        filtered = []
        for ds in datasets:
            reviews = []
            for r in ds.reviews:
                if not r.date:
                    continue
                try:
                    review_date = datetime.strptime(r.date, "%Y-%m-%d").date()
                except ValueError:
                    continue
                if self.date_from and review_date < self.date_from:
                    continue
                if self.date_to and review_date > self.date_to:
                    continue
                reviews.append(r)

            if reviews:
                filtered.append(
                    Dataset(
                        id=ds.id,
                        brand=ds.brand,
                        category=ds.category,
                        product=ds.product,
                        source=ds.source,
                        uploaded_at=ds.uploaded_at,
                        reviews=reviews,
                    )
                )
        return filtered

    def get_sources(self) -> list[dict]:
        """Возвращает список источников с количеством отзывов в выбранном диапазоне."""
        datasets = self.get_selected_datasets()
        datasets = self.apply_date_filter(datasets)

        sources_map = {}
        for ds in datasets:
            source_name = ds.source or "Неизвестный источник"
            # Считаем количество отзывов с этого источника
            review_count = len(ds.reviews)
            sources_map[source_name] = sources_map.get(source_name, 0) + review_count

        return [
            {"name": name, "count": count, "url": "#"}
            for name, count in sources_map.items()
        ]

    def get_dashboard_data(self):
        datasets = self.get_selected_datasets()
        if not datasets:
            return None, None

        datasets = self.apply_date_filter(datasets)
        if not datasets:
            return None, None

        analytics = AnalyticsService(datasets)
        return analytics.get_full_dashboard(), analytics.all_reviews