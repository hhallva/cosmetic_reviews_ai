import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

import app.core.constants as consts
from views.dashboard.dashboard import render_dashboard
from views.landing import render_landing
from views.reports_list import render_reports_list

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="VSA",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ГЛОБАЛЬНЫЕ CSS СТИЛИ ---
st.markdown("""
    <style>
    .hide-sidebar [data-testid="stSidebar"] { display: none !important; }
    .show-sidebar [data-testid="stSidebar"] { display: block !important; }

    .section-header { 
        font-size: 1.3rem; font-weight: 700; color: #212529; 
        margin-bottom: 1rem; border-bottom: 2px solid #d63384; padding-bottom: 0.5rem;
    }
    .review-card {
        background-color: #ffffff; border: 1px solid #e9ecef; border-left: 4px solid #d63384;
        border-radius: 6px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .source-card {
        background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px;
        padding: 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;
    }
    .ai-block {
        background: linear-gradient(135deg, #fff0f6 0%, #f8f9fa 100%);
        border-radius: 8px; padding: 20px; border: 1px solid #fcc2d7;
    }
    [data-theme="dark"] .review-card, [data-theme="dark"] .source-card { background-color: #262730; border-color: #4a4b57; }
    [data-theme="dark"] .ai-block { background: linear-gradient(135deg, #2c2e3a 0%, #1e1e24 100%); border-color: #4a4b57; }
    </style>
""", unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ (РОУТИНГ) ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "dashboard_tab" not in st.session_state:
    st.session_state.dashboard_tab = "📊 Дашборд"
if "selected_product" not in st.session_state:
    st.session_state.selected_product = ""
if "report_data" not in st.session_state:
    st.session_state.report_data = None

# Подготовка данных для комбобокса
all_options = [f"{line} — {product}" for line, products in consts.PRODUCTS.items() for product in products]

# --- РОУТИНГ ---
if st.session_state.page == "landing":
    st.markdown('<div class="hide-sidebar"></div>', unsafe_allow_html=True)
    render_landing(all_options)

elif st.session_state.page == "reports_list":
    st.markdown('<div class="hide-sidebar"></div>', unsafe_allow_html=True)
    render_reports_list()

elif st.session_state.page == "dashboard":
    st.markdown('<div class="show-sidebar"></div>', unsafe_allow_html=True)
    render_dashboard()