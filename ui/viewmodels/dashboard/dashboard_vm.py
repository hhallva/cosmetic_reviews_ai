# app/viewmodels/dashboard_vm.py
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

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
    dashboard_tab: str = "Дашборд"
    selected_dataset_ids: list[str] = field(default_factory=list)
    date_from: object = None
    date_to: object = None

    def __post_init__(self):
        self.datasets_meta = self.manager.get_datasets_by_product(self.brand, self.product)
        if not self.selected_dataset_ids:
            self.selected_dataset_ids = [ds.id for ds in self.datasets_meta]

    def get_available_datasets(self):
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
            filtered_reviews = []
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
                filtered_reviews.append(r)

            if filtered_reviews:
                filtered.append(
                    Dataset(
                        id=ds.id,
                        brand=ds.brand,
                        category=ds.category,
                        product=ds.product,
                        source=ds.source,
                        uploaded_at=ds.uploaded_at,
                        reviews=filtered_reviews,
                    )
                )
        return filtered

    def get_dashboard_data(self):
        datasets = self.get_selected_datasets()
        if not datasets:
            return None, None

        datasets = self.apply_date_filter(datasets)
        if not datasets:
            return None, None

        analytics = AnalyticsService(datasets)
        return analytics.get_full_dashboard(), analytics.all_reviews

    def set_tab(self, tab_name: str):
        self.dashboard_tab = tab_name

    def set_selected_datasets(self, ids: list[str]):
        self.selected_dataset_ids = ids

    def set_dates(self, date_from, date_to):
        self.date_from = date_from
        self.date_to = date_to