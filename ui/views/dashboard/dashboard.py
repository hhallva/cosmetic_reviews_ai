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

    if "dialog_delete_id" not in st.session_state:
        st.session_state.dialog_delete_id = None

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
                    col1, col2, col3 = st.columns([0.7, 0.1, 0.2])

                    with col1:
                        checked = st.checkbox(
                            f"{ds_meta.id}",
                            value=ds_meta.id in vm.selected_dataset_ids,
                            key=f"ds_{ds_meta.id}",
                        )

                    with col2:
                        # Можно добавить информационную иконку
                        if ds_meta.reviews_count > 0:
                            st.caption(f"📝 {ds_meta.reviews_count}")

                    with col3:
                        # Кнопка удаления открывает диалог
                        if st.button("🗑️", key=f"delete_{ds_meta.id}", help="Удалить датасет"):
                            st.session_state.dialog_delete_id = ds_meta.id
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

    if st.session_state.dialog_delete_id:
        ds_id_to_delete = st.session_state.dialog_delete_id

        # Находим датасет для отображения информации из сохраненного списка
        ds_to_delete = next((ds for ds in vm.get_datasets() if ds.id == ds_id_to_delete), None)

        if ds_to_delete:
            @st.dialog(f"Удаление датасета", width="small")
            def confirm_delete_dialog():
                st.warning(f"Вы действительно хотите удалить датасет **{ds_to_delete.id}**?")
                st.caption(f"{ds_to_delete.reviews_count} отзывов")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Да, удалить", type="primary", use_container_width=True):
                        vm.delete_dataset(ds_id_to_delete)
                        st.session_state.dialog_delete_id = None
                        # Очищаем кэш датасетов
                        st.session_state.datasets_list = []
                        st.rerun()
                with col2:
                    if st.button("Отмена", use_container_width=True):
                        st.session_state.dialog_delete_id = None
                        st.rerun()

            confirm_delete_dialog()


    if vm.dashboard_tab == "Дашборд":
        render_metrics_view(dashboard_data, all_reviews)
    elif vm.dashboard_tab == "Отзывы":
        render_reviews_view(all_reviews)