import streamlit as st
from pathlib import Path

from app.services.dataset_manager import DatasetManager

DATASETS_DIR = Path("data/datasets")


def render_brand_page():
    manager = DatasetManager(DATASETS_DIR)
    brand = st.session_state.get("selected_brand")

    if not brand:
        st.warning("Бренд не выбран.")
        if st.button("← На главную"):
            st.session_state.page = "landing"
            st.rerun()
        return

    st.header(f"🏢 {brand}")
    st.divider()

    # Кнопка назад
    if st.button("← Назад к брендам"):
        st.session_state.page = "landing"
        st.rerun()

    # --- ФИЛЬТРЫ ---
    col1, col2 = st.columns(2)

    with col1:
        categories = manager.get_categories(brand)
        selected_category = st.selectbox(
            "Фильтр по категории",
            options=["Все"] + categories,
        )

    with col2:
        search = st.text_input("🔍 Поиск продукта", placeholder="Название продукта...")

    # --- ПРОДУКТЫ ---
    products = manager.get_products_by_brand(brand)

    # Применяем фильтры
    if selected_category != "Все":
        products = [p for p in products if p.category == selected_category]

    if search:
        products = [p for p in products if search.lower() in p.product.lower()]

    if not products:
        st.info("Нет продуктов, соответствующих фильтрам.")
        return

    st.markdown(f"**Найдено продуктов:** {len(products)}")
    st.markdown("<br>", unsafe_allow_html=True)

    # Карточки продуктов
    cols = st.columns(3)
    for idx, product_stats in enumerate(products):
        with cols[idx % 3]:
            stars = "⭐" * int(product_stats.avg_rating) + "☆" * (5 - int(product_stats.avg_rating))
            st.markdown(f"""
            <div class="product-card">
                <h4>🛍️ {product_stats.product}</h4>
                <div style="color: #6c757d; font-size: 0.9rem;">{product_stats.category}</div>
                <div style="margin: 8px 0;">{stars} ({product_stats.avg_rating}/5.0)</div>
                <div class="stats">
                    <div>📦 Датасетов: <strong>{product_stats.datasets_count}</strong></div>
                    <div>📝 Отзывов: <strong>{product_stats.reviews_count}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"📊 Анализ", key=f"product_{product_stats.product}"):
                st.session_state.selected_brand = brand
                st.session_state.selected_product = product_stats.product
                st.session_state.page = "dashboard"
                st.rerun()