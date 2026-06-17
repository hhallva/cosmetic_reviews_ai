import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from viewmodels.dashboard.dashboard_vm import DashboardViewModel
from ui.views.dashboard.dashboard import render_dashboard
from viewmodels.landing_vm import LandingViewModel
from views.landing.landing import render_landing


def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "dashboard_tab" not in st.session_state:
        st.session_state.dashboard_tab = "Дашборд"
    if "selected_brand" not in st.session_state:
        st.session_state.selected_brand = None
    if "selected_product" not in st.session_state:
        st.session_state.selected_product = None
    if "selected_datasets" not in st.session_state:
        st.session_state.selected_datasets = []


def main():
    init_state()

    if st.session_state.page == "landing":
        vm = LandingViewModel()
        render_landing(vm)

    elif st.session_state.page == "dashboard":
        vm = DashboardViewModel(
            brand=st.session_state.get("selected_brand"),
            product=st.session_state.get("selected_product")
        )
        render_dashboard(vm)


if __name__ == "__main__":
    main()