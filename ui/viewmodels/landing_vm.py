import sys
from pathlib import Path
from typing import Optional
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.dataset_manager import DatasetManager

DATASETS_DIR = Path("data/datasets")
MANUAL_INPUT = "+ Ввести вручную"

class LandingViewModel:
    def __init__(self):
        self.manager = DatasetManager(DATASETS_DIR)
        self.datasets = self.manager.list_datasets()

        self.all_brands = sorted(set(ds.brand for ds in self.datasets))
        self.all_categories = sorted(set(ds.category for ds in self.datasets))
        self.all_products = sorted(set(ds.product for ds in self.datasets))
        self.all_sources = sorted(set(ds.source for ds in self.datasets))

        self.brand_value = ""
        self.category_value = ""
        self.product_value = ""
        self.source_value = "unknown"
        self.uploaded_file = None

        self.error: Optional[str] = None
        self.success: Optional[str] = None

    def get_product_options(self):
        if self.brand_value and self.category_value:
            filtered_products = sorted(
                {
                    ds.product
                    for ds in self.datasets
                    if ds.brand.strip().lower() == self.brand_value.strip().lower()
                    and ds.category.strip().lower() == self.category_value.strip().lower()
                }
            )
            return filtered_products + [MANUAL_INPUT] if filtered_products else [MANUAL_INPUT]
        return [MANUAL_INPUT]

    def get_brand_options(self):
        return self.all_brands + [MANUAL_INPUT]

    def get_category_options(self):
        return self.all_categories + [MANUAL_INPUT]

    def get_source_options(self):
        return self.all_sources + [MANUAL_INPUT]

    def can_upload(self):
        return bool(
            self.brand_value
            and self.category_value
            and self.product_value
            and self.source_value
            and self.uploaded_file is not None
        )

    def set_brand(self, value: str):
        self.brand_value = value.strip()

    def set_category(self, value: str):
        self.category_value = value.strip()

    def set_product(self, value: str):
        self.product_value = value.strip()

    def set_source(self, value: str):
        self.source_value = value.strip() or "unknown"

    def set_uploaded_file(self, value):
        self.uploaded_file = value

    def upload(self):
        if not self.brand_value or not self.category_value or not self.product_value:
            self.error = "Заполните все поля: бренд, категорию и продукт"
            return None

        if self.uploaded_file is None:
            self.error = "Загрузите JSON-файл с отзывами"
            return None

        tmp_path = DATASETS_DIR / f"tmp_{self.uploaded_file.name}"
        tmp_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(tmp_path, "wb") as f:
                f.write(self.uploaded_file.getbuffer())

            meta = self.manager.upload_dataset(
                reviews_file=tmp_path,
                brand=self.brand_value,
                category=self.category_value,
                product=self.product_value,
                source=self.source_value,
            )
            self.success = f"✅ Загружен: {meta.brand} → {meta.product} ({meta.reviews_count} отзывов)"
            self.error = None

            st.session_state.selected_brand = meta.brand
            st.session_state.selected_product = meta.product
            st.session_state.page = "dashboard"
            st.session_state.dashboard_tab = "📊 Дашборд"

            return meta
        except Exception as e:
            self.error = f"❌ Ошибка загрузки: {e}"
            return None
        finally:
            if tmp_path.exists():
               tmp_path.unlink()

