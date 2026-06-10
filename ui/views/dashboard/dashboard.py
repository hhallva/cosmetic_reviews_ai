# app/ui/views/dashboard/dashboard.py
from pathlib import Path

import streamlit as st

from viewmodels.dashboard.dashboard_vm import DashboardViewModel
from views.dashboard.metrics.metrics import render_metrics_view
from views.dashboard.reviews.reviews import render_reviews_view
from views.dashboard.sources.sources import render_sources_view


def render_dashboard(vm: DashboardViewModel):
    css_file = Path(__file__).parent / "dashboard.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.sidebar.title(vm.brand)
    st.sidebar.text(f"Продукт: {vm.product}")

    st.sidebar.divider()

    st.sidebar.text("Фильтр по датам", help="Укажите диапазон дат для отзывов, для анализа периодов.")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        date_from = st.date_input("Начальная дата", value=None, key="dashboard_date_from")
    with col2:
        date_to = st.date_input("Конечная дата", value=None, key="dashboard_date_to")
    vm.set_dates(date_from, date_to)

    st.sidebar.divider()

    st.sidebar.text("Датасеты")
    selected_ids = []
    for ds_meta in vm.get_available_datasets():
        checked = st.sidebar.checkbox(
            f"{ds_meta.id} ({ds_meta.reviews_count} отзывов)",
            value=ds_meta.id in vm.selected_dataset_ids,
            key=f"ds_{ds_meta.id}",
        )
        if checked:
            selected_ids.append(ds_meta.id)
    vm.set_selected_datasets(selected_ids)

    st.sidebar.divider()
    if st.sidebar.button(
        "Дашборд",
        use_container_width=True,
        type="primary" if vm.dashboard_tab == "Дашборд" else "secondary",
    ):
        vm.set_tab("Дашборд")
        st.rerun()

    if st.sidebar.button(
        "Отзывы",
        use_container_width=True,
        type="primary" if vm.dashboard_tab == "Отзывы" else "secondary",
    ):
        vm.set_tab("Отзывы")
        st.rerun()

    if st.sidebar.button(
        "Источники",
        use_container_width=True,
        type="primary" if vm.dashboard_tab == "Источники" else "secondary",
    ):
        vm.set_tab("Источники")
        st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("← К продуктам", use_container_width=True):
        st.session_state.page = "brand_page"
        st.rerun()

    dashboard_data, all_reviews = vm.get_dashboard_data()
    if not dashboard_data:
        st.warning("Нет данных для отображения.")
        return

    if vm.dashboard_tab == "Дашборд":
        render_metrics_view(dashboard_data, all_reviews)
    elif vm.dashboard_tab == "Отзывы":
        render_reviews_view(all_reviews)
    elif vm.dashboard_tab == "Источники":
        sources = [
            {"name": src, "count": count, "url": "#"}
            for src, count in dashboard_data["sources"].items()
        ]
        render_sources_view(sources, vm.product)