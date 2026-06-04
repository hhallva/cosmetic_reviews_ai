import streamlit as st

from .metrics import render_metrics_view
from .reviews import render_reviews_view
from .sources import render_sources_view


def render_dashboard():
    # --- 1. БОКОВОЕ МЕНЮ ---
    with st.sidebar:
        st.title("💄 VS Analytics")
        st.markdown(f"**Текущий отчет:**\n*{st.session_state.selected_product}*")
        st.divider()

        # Кнопки навигации с подсветкой активной
        if st.button("📊 Дашборд", use_container_width=True,
                     type="primary" if st.session_state.dashboard_tab == "📊 Дашборд" else "secondary"):
            st.session_state.dashboard_tab = "📊 Дашборд"
            st.rerun()

        if st.button("📝 Отзывы", use_container_width=True,
                     type="primary" if st.session_state.dashboard_tab == "📝 Отзывы" else "secondary"):
            st.session_state.dashboard_tab = "📝 Отзывы"
            st.rerun()

        if st.button("🔗 Источники", use_container_width=True,
                     type="primary" if st.session_state.dashboard_tab == "🔗 Источники" else "secondary"):
            st.session_state.dashboard_tab = "🔗 Источники"
            st.rerun()

        st.divider()
        if st.button("🏠 На главную", type="secondary", use_container_width=True):
            st.session_state.page = "landing"
            st.session_state.selected_product = ""
            st.session_state.report_data = None
            st.rerun()

    # --- 2. ОСНОВНОЙ КОНТЕНТ ---
    if not st.session_state.report_data:
        st.warning("Нет данных для отображения.")
        return

    # Распаковываем данные из кортежа
    metrics, segments_df, trends_df, sources_list, reviews_list, ai_text = st.session_state.report_data
    product_name = st.session_state.selected_product

    # --- 3. РОУТИНГ ВНУТРИ ДАШБОРДА ---
    if st.session_state.dashboard_tab == "📊 Дашборд":
        render_metrics_view(metrics, segments_df, trends_df, ai_text, product_name)

    elif st.session_state.dashboard_tab == "📝 Отзывы":
        render_reviews_view(reviews_list, product_name)

    elif st.session_state.dashboard_tab == "🔗 Источники":
        render_sources_view(sources_list, product_name)