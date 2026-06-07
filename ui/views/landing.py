import streamlit as st
from pathlib import Path

def render_landing(all_options):
    css_file = Path(__file__).parent / "landing.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Файл стилей landing.css не найден.")

    def on_analyze_click():
        product = st.session_state.get("landing_product_select")
        if product:
            from utils.data_generator import generate_mock_data

            st.session_state.selected_product = product
            st.session_state.report_data = generate_mock_data(product)
            st.session_state.page = "dashboard"
            st.session_state.dashboard_tab = "📊 Дашборд"
        else:
            st.session_state.landing_error = "Пожалуйста, выберите товар из списка."

    def on_reports_click():
        st.session_state.page = "reports_list"

    c1, c2, c3 = st.columns([2, 2, 2])

    with c2:
        st.markdown('<div class="landing-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="main-title">Vivienne Sabo Analytics</h1>', unsafe_allow_html=True, text_alignment="center")
        st.markdown('<p class="subtitle">Система интеллектуального анализа отзывов</p>', unsafe_allow_html=True, text_alignment="center")

        # Поле ввода и кнопка в одной строке
        col_input, col_btn = st.columns([4, 1])

        with col_input:
            product = st.selectbox(
                "Поиск товара",
                label_visibility="collapsed",
                options=all_options,
                index=None,
                key="landing_product_select",
                placeholder="Начните вводить название товара...",
            )

        with col_btn:
            st.button(
                "Анализ",
                type="primary",
                use_container_width=True,
                on_click=on_analyze_click
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get("landing_error"):
            st.warning(st.session_state.landing_error)
            st.session_state.landing_error = None

        st.button("Предыдущие отчеты",
                  use_container_width=True,
                  on_click=on_reports_click)

        st.markdown('</div>', unsafe_allow_html=True)
