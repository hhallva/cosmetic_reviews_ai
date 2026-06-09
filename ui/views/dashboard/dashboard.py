import streamlit as st
from .metrics import render_metrics_view
from .reviews import render_reviews_view


def render_dashboard():
    # --- CSS ДЛЯ УБРАНИЯ ОТСТУПОВ ---
    st.markdown("""
        <style>
        .st-emotion-cache-1w723zb {
            max-width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- БОКОВОЕ МЕНЮ ---
    with st.sidebar:
        st.title("💄 VS Analytics")

        # Показываем выбранные датасеты
        datasets = st.session_state.get("selected_datasets", [])
        if datasets:
            st.markdown("**Выбранные датасеты:**")
            for ds in datasets:
                st.caption(f"• {ds.brand} — {ds.product}")
                st.caption(f"  ({ds.reviews_count} отзывов)")
        st.divider()

        # Навигация
        if st.button(
            "Дашборд",
            use_container_width=True,
            type="primary" if st.session_state.dashboard_tab == "Дашборд" else "secondary",
        ):
            st.session_state.dashboard_tab = "Дашборд"
            st.rerun()

        if st.button(
            "Отзывы",
            use_container_width=True,
            type="primary" if st.session_state.dashboard_tab == "Отзывы" else "secondary",
        ):
            st.session_state.dashboard_tab = "Отзывы"
            st.rerun()

        st.divider()

        if st.button("На главную", type="secondary", use_container_width=True):
            st.session_state.page = "landing"
            st.session_state.selected_datasets = []
            st.session_state.dashboard_data = None
            st.session_state.all_reviews = []
            st.rerun()

    # --- ОСНОВНОЙ КОНТЕНТ ---
    dashboard_data = st.session_state.get("dashboard_data")
    all_reviews = st.session_state.get("all_reviews", [])

    if not dashboard_data:
        st.warning("Нет данных для отображения.")
        return

    # Роутинг
    if st.session_state.dashboard_tab == "Дашборд":
        render_metrics_view(dashboard_data)
    elif st.session_state.dashboard_tab == "Отзывы":
        render_reviews_view(all_reviews)