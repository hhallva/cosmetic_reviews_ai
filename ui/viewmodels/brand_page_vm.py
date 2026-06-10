import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.dataset_manager import DatasetManager

DATASETS_DIR = Path("data/datasets")

class BrandPageViewModel:
    def __init__(self, brand: str):
        self.manager = DatasetManager(DATASETS_DIR)
        self.brand = brand

        self.categories = self.manager.get_categories(brand)
        self.selected_category = "Все"
        self.search = ""

    def get_products(self):
        products = self.manager.get_products_by_brand(self.brand)

        if self.selected_category != "Все":
            products = [p for p in products if p.category == self.selected_category]

        if self.search:
            query = self.search.strip().lower()
            products = [p for p in products if query in p.product.lower()]

        return products

    def set_category(self, value: str):
        self.selected_category = value

    def set_search(self, value: str):
        self.search = value.strip()

    def go_to_dashboard(self, product_name: str):
        st.session_state.selected_brand = self.brand
        st.session_state.selected_product = product_name
        st.session_state.page = "dashboard"

    @staticmethod
    def go_to_landing():
        st.session_state.page = "landing"
        st.session_state.selected_product = None
        st.session_state.selected_datasets = []

