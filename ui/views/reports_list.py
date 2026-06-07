import streamlit as st
from pathlib import Path
from utils.data_generator import generate_mock_data, MOCK_SAVED_REPORTS


def render_reports_list():
    css_file = Path(__file__).parent / "reports_list.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    if "show_filters" not in st.session_state:
        st.session_state.show_filters = False
    if "report_search" not in st.session_state:
        st.session_state.report_search = ""
    if "report_date_from" not in st.session_state:
        st.session_state.report_date_from = None
    if "report_date_to" not in st.session_state:
        st.session_state.report_date_to = None

    def on_back_click():
        st.session_state.page = "landing"

    def on_report_click(report: dict):
        st.session_state.selected_product = report["product"]
        st.session_state.report_data = generate_mock_data(report["product"])
        st.session_state.page = "dashboard"
        st.session_state.dashboard_tab = "📊 Дашборд"

    def on_search_click():
        pass

    def on_toggle_filters():
        st.session_state.show_filters = not st.session_state.show_filters

    def on_reset_click():
        st.session_state.report_search = ""
        st.session_state.report_date_from = None
        st.session_state.report_date_to = None
        st.session_state.show_filters = False

    st.markdown('<div class="reports-header">', unsafe_allow_html=True)
    st.header("📂 Архив отчетов")

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    st.button("← Назад к поиску", on_click=on_back_click)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="search-block">', unsafe_allow_html=True)

    col_search, col_btn_find, col_btn_filters, col_btn_reset, c1 = st.columns([4, 1, 0.5, 0.5, 4])

    with col_search:
        search_query = st.text_input(
            "Поиск по названию",
            placeholder="Например: Cabaret, Тушь, Помада...",
            key="report_search",
            label_visibility="collapsed"
        )

    with col_btn_find:
        st.button(
            "Найти",
            on_click=on_search_click,
            key="search_btn",
            type="primary",
            use_container_width=True
        )

    with col_btn_filters:
        st.button(
            "Фильтры",
            on_click=on_toggle_filters,
            key="filters_btn",
            type="secondary",
            use_container_width=True
        )

    with col_btn_reset:
        st.button(
            "Сбросить",
            on_click=on_reset_click,
            key="reset_btn",
            type="secondary",
            use_container_width=True
        )

    # --- БЛОК ФИЛЬТРОВ ПО ДАТЕ (показывается/скрывается) ---
    if st.session_state.show_filters:
        st.markdown('<div class="filters-block">', unsafe_allow_html=True)

        date_col1, date_col2 = st.columns(2)
        with date_col1:
            date_from = st.date_input(
                "Дата от",
                value=st.session_state.report_date_from,
                key="report_date_from",
                format="DD.MM.YYYY"
            )
        with date_col2:
            date_to = st.date_input(
                "Дата до",
                value=st.session_state.report_date_to,
                key="report_date_to",
                format="DD.MM.YYYY"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # --- ФИЛЬТРАЦИЯ СПИСКА ---
    filtered_reports = MOCK_SAVED_REPORTS[:]

    # Фильтр по названию (регистронезависимый)
    if search_query:
        query_lower = search_query.lower()
        filtered_reports = [
            r for r in filtered_reports
            if query_lower in r["product"].lower()
        ]

    # Фильтр по дате "от"
    if st.session_state.report_date_from is not None:
        filtered_reports = [
            r for r in filtered_reports
            if r["date"].date() >= st.session_state.report_date_from
        ]

    # Фильтр по дате "до"
    if st.session_state.report_date_to is not None:
        filtered_reports = [
            r for r in filtered_reports
            if r["date"].date() <= st.session_state.report_date_to
        ]

    # --- СЧЕТЧИК РЕЗУЛЬТАТОВ ---
    total_count = len(MOCK_SAVED_REPORTS)
    filtered_count = len(filtered_reports)

    has_active_filters = bool(
        search_query) or st.session_state.report_date_from is not None or st.session_state.report_date_to is not None

    if has_active_filters:
        st.markdown(
            f'<div class="results-counter">Найдено: <strong>{filtered_count}</strong> из {total_count} отчетов</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="results-counter">Всего отчетов: <strong>{total_count}</strong></div>',
            unsafe_allow_html=True
        )


    # --- ОТОБРАЖЕНИЕ СПИСКА ---
    if not filtered_reports:
        st.info("Отчеты по заданным критериям не найдены. Попробуйте изменить параметры поиска.")
    else:
        for report in filtered_reports:
            btn_key = f"rep_{report['product']}_{report['date'].strftime('%Y%m%d')}"

            st.button(
                f"{report['product']} ({report['date'].strftime('%d.%m.%Y')})",
                key=btn_key,
                on_click=on_report_click,
                args=(report,),
                type="secondary",
                use_container_width=True
            )
