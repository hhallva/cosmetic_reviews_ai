import streamlit as st
from utils.data_generator import generate_mock_data, MOCK_SAVED_REPORTS


def render_reports_list():
    st.header("📂 Архив отчетов")
    if st.button("← Назад к поиску", type="secondary"):
        st.session_state.page = "landing"
        st.rerun()
    st.divider()

    for report_name in MOCK_SAVED_REPORTS:
        if st.button(report_name, key=f"rep_{report_name}", use_container_width=True):
            clean_name = report_name.split(" (")[0]
            st.session_state.selected_product = clean_name
            st.session_state.report_data = generate_mock_data(clean_name)
            st.session_state.page = "dashboard"
            st.session_state.dashboard_tab = "📊 Дашборд"
            st.rerun()