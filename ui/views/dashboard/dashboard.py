from pathlib import Path

import streamlit as st
from datetime import datetime

from .metrics import render_metrics_view
from .reviews import render_reviews_view
from app.services.dataset_manager import DatasetManager
from app.services.analytics import AnalyticsService

DATASETS_DIR = Path("data/datasets")

def render_dashboard():
    manager = DatasetManager(DATASETS_DIR)
    brand = st.session_state.get("selected_brand")
    product = st.session_state.get("selected_product")


    if not brand or not product:
        st.warning("Не выбран бренд или продукт.")
        return

    # --- БОКОВОЕ МЕНЮ ---
    with st.sidebar:
        st.title("💄 Analytics")
        st.markdown(f"**Бренд:** {brand}")
        st.markdown(f"**Продукт:** {product}")
        st.divider()
        st.markdown("**📦 Датасеты:**")
        datasets_meta = manager.get_datasets_by_product(brand, product)

        selected_datasets = []
        for ds_meta in datasets_meta:
            checked = st.checkbox(
                f"{ds_meta.id} ({ds_meta.reviews_count} отзывов)",
                value=True,
                key=f"ds_{ds_meta.id}",
            )
            if checked:
                selected_datasets.append(ds_meta.id)

        st.divider()

        # Фильтр по датам
        st.markdown("**📅 Фильтр по датам:**")
        date_from = st.date_input("С", value=None)
        date_to = st.date_input("По", value=None)

        st.divider()
        # Навигация
        if st.button("Дашборд", use_container_width=True,
                     type="primary" if st.session_state.dashboard_tab == "Дашборд" else "secondary"):
            st.session_state.dashboard_tab = "Дашборд"
            st.rerun()

        if st.button("Отзывы", use_container_width=True,
                     type="primary" if st.session_state.dashboard_tab == "Отзывы" else "secondary"):
            st.session_state.dashboard_tab = "Отзывы"
            st.rerun()

        st.divider()

        if st.button("← К продуктам", use_container_width=True):
            st.session_state.page = "brand_page"
            st.rerun()

            # --- ОСНОВНОЙ КОНТЕНТ ---
            # Загружаем выбранные датасеты
        datasets = []
        for ds_id in selected_datasets:
            ds = manager.get_dataset(ds_id)
            if ds:
                datasets.append(ds)

        if not datasets:
            st.warning("Нет выбранных датасетов для анализа.")
            return

        # Применяем фильтр по датам
        if date_from or date_to:
            filtered_datasets = []
            for ds in datasets:
                filtered_reviews = []
                for r in ds.reviews:
                    if r.date:
                        try:
                            review_date = datetime.strptime(r.date, "%Y-%m-%d").date()
                            if date_from and review_date < date_from:
                                continue
                            if date_to and review_date > date_to:
                                continue
                            filtered_reviews.append(r)
                        except ValueError:
                            continue

                if filtered_reviews:
                    from app.models.dataset import Dataset
                    filtered_ds = Dataset(
                        id=ds.id,
                        brand=ds.brand,
                        category=ds.category,
                        product=ds.product,
                        source=ds.source,
                        uploaded_at=ds.uploaded_at,
                        reviews=filtered_reviews,
                    )
                    filtered_datasets.append(filtered_ds)
            datasets = filtered_datasets

        if not datasets:
            st.warning("Нет отзывов, соответствующих фильтрам.")
            return

        # Считаем аналитику
        analytics = AnalyticsService(datasets)
        dashboard_data = analytics.get_full_dashboard()

        # Сохраняем в session_state
        st.session_state.dashboard_data = dashboard_data
        st.session_state.all_reviews = analytics.all_reviews

        # Роутинг
        if st.session_state.dashboard_tab == "Дашборд":
            render_metrics_view(dashboard_data)
        elif st.session_state.dashboard_tab == "Отзывы":
            render_reviews_view(analytics.all_reviews)