#views/dasboard/sourses.py

import streamlit as st

def render_sources_view(sources_list: list, product_name: str):
    st.header(f"🔗 Источники данных: {product_name}")
    st.divider()
    st.markdown("Отзывы были агрегированы со следующих платформ.")
    st.markdown("<br>", unsafe_allow_html=True)

    for src in sources_list:
        st.markdown(f"""
        <div class="source-card">
            <div>
                <strong style="font-size: 1.1rem;">🌐 {src['name']}</strong>
                <div style="color: #6c757d; font-size: 0.9rem; margin-top: 4px;">
                    Собрано отзывов: <strong>{src['count']}</strong>
                </div>
            </div>
            <a href="{src['url']}" target="_blank" style="text-decoration: none;">
                <button style="background-color: #d63384; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;">
                    Перейти ↗
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)