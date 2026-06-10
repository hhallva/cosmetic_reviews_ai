# app/ui/views/brand_page.py
from pathlib import Path

import streamlit as st

from viewmodels.brand_page_vm import BrandPageViewModel

def render_brand_page(vm: BrandPageViewModel):
    css_file = Path(__file__).parent / "brand_page.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    brand = vm.brand

    if not brand:
        st.warning("Бренд не выбран.")
        st.button("← На главную", on_click=vm.go_to_landing)

    st.header(f"{vm.brand}",text_alignment="center")
    st.button("← Назад к брендам", on_click=vm.go_to_landing)

    col1, col2 = st.columns(2)

    with col1:
        selected_category = st.selectbox(
            "Фильтр по категории",
            options=["Все"] + vm.categories,
            index=0,
            key="brand_page_category",
        )
        vm.set_category(selected_category)

    with col2:
        search = st.text_input(
            "🔍 Поиск продукта",
            placeholder="Название продукта...",
            key="brand_page_search",
        )
        vm.set_search(str(search))

    products = vm.get_products()

    if not products:
        st.info("Нет продуктов, соответствующих фильтрам.")
        return

    st.divider()

    cols = st.columns(3)
    for idx, product_stats in enumerate(products):
        with cols[idx % 3]:
            with st.container(border=True):
                stars = "⭐" * int(product_stats.avg_rating) + "☆" * (5 - int(product_stats.avg_rating))

                st.subheader(product_stats.product)
                c1, c2 = st.columns(2)
                with c1:
                    st.text(product_stats.category)
                    st.text(f"{stars} ({product_stats.avg_rating}/5.0)")
                with c2:
                    st.text(f"Датасетов: {product_stats.datasets_count}")
                    st.text(f"Отзывов: {product_stats.reviews_count}")
                st.button(
                    "Подробнее",
                    key=f"product_{product_stats.product}_{idx}",
                    use_container_width=True,
                    on_click=vm.go_to_dashboard,
                    args=(product_stats.product,)
                )


