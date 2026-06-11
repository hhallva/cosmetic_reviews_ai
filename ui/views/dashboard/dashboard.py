# app/ui/views/dashboard/dashboard.py
from pathlib import Path

import streamlit as st

from viewmodels.dashboard.dashboard_vm import DashboardViewModel
from views.dashboard.metrics.metrics import render_metrics_view
from views.dashboard.reviews.reviews import render_reviews_view


def render_dashboard(vm: DashboardViewModel):
    css_file = Path(__file__).parent / "dashboard.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.title(vm.brand)
        st.text(f"Продукт: {vm.product}")

        st.divider()
        st.text("Фильтр по датам", help="Укажите диапазон дат для отзывов, для анализа периодов.")

        min_date = vm.available_min_date
        max_date = vm.available_max_date

        if min_date and max_date:
            col1, col2 = st.columns(2)
            with col1:
                date_from = st.date_input(
                    "Начальная дата",
                    value=vm.date_from or min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="dashboard_date_from",
                )
            with col2:
                date_to = st.date_input(
                    "Конечная дата",
                    value=vm.date_to or max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="dashboard_date_to",
                )
        else:
            date_from = st.date_input("Начальная дата", value=None, key="dashboard_date_from")
            date_to = st.date_input("Конечная дата", value=None, key="dashboard_date_to")
        vm.set_dates(date_from, date_to)

        st.divider()
        st.text("Датасеты")

        grouped_datasets = vm.get_datasets_grouped_by_source()
        selected_ids = []

        for source_name, datasets in grouped_datasets.items():
            total_reviews = sum(ds.reviews_count for ds in datasets)

            with st.expander(
                    f"**{source_name}** | Датасетов: {len(datasets)}, Отзывов: {total_reviews}",
                    expanded=False,
                    key=f"expander_{source_name}"
            ):

                for ds_meta in datasets:
                    row1, row2 = st.columns([5, 1])

                    with row1:
                        checked = st.checkbox(
                            f"{ds_meta.id} ({ds_meta.reviews_count} отзывов)",
                            value=ds_meta.id in vm.selected_dataset_ids,
                            key=f"ds_{ds_meta.id}",
                        )

                    with row2:
                        if st.button("🗑️", key=f"delete_{ds_meta.id}", help="Удалить датасет"):
                            st.session_state[f"confirm_delete_{ds_meta.id}"] = True

                    if st.session_state.get(f"confirm_delete_{ds_meta.id}", False):
                        st.warning(f"Удалить датасет {ds_meta.id}?")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Да", key=f"confirm_yes_{ds_meta.id}"):
                                vm.delete_dataset(ds_meta.id)
                                st.session_state[f"confirm_delete_{ds_meta.id}"] = False
                                st.rerun()
                        with c2:
                            if st.button("Нет", key=f"confirm_no_{ds_meta.id}"):
                                st.session_state[f"confirm_delete_{ds_meta.id}"] = False
                                st.rerun()

                    if checked:
                        selected_ids.append(ds_meta.id)

        vm.set_selected_datasets(selected_ids)

        st.divider()
        if st.button(
                "Дашборд",
                use_container_width=True,
                type="primary" if vm.dashboard_tab == "Дашборд" else "secondary",
        ):
            vm.set_tab("Дашборд")
            st.rerun()

        if st.button(
                "Отзывы",
                use_container_width=True,
                type="primary" if vm.dashboard_tab == "Отзывы" else "secondary",
        ):
            vm.set_tab("Отзывы")
            st.rerun()

        st.divider()
        if st.button("← К продуктам", use_container_width=True):
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