import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from ui.views.landing import render_landing
from ui.views.brand_page import render_brand_page
from ui.views.dashboard.dashboard import render_dashboard


def main():
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "dashboard_tab" not in st.session_state:
        st.session_state.dashboard_tab = "Дашборд"

    if st.session_state.page == "landing":
        render_landing()
    elif st.session_state.page == "brand_page":
        render_brand_page()
    elif st.session_state.page == "dashboard":
        render_dashboard()


if __name__ == "__main__":
    main()