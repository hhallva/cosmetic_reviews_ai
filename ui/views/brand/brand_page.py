# app/ui/views/brand_page.py
from pathlib import Path

import streamlit as st

from viewmodels.brand_page_vm import BrandPageViewModel

def render_rank_card(position: int, product, rating: float, kind: str) -> None:
    """
    kind: 'best' или 'worst'
    """
    if kind == "best":
        # Для лучших — медали
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        medal = medals.get(position, f"<span style='color:#6c757d;font-weight:600'>#{position}</span>")
        medal_html = f'<div class="rank-medal">{medal}</div>'
    else:
        # Для худших — красные кружки с номерами
        medal_html = f'<div class="rank-medal"><span class="rank-number">{position}</span></div>'

    # Звёзды: 5 символов, заполняем пропорционально рейтингу
    max_stars = 5
    filled = round(rating) if rating <= max_stars else max_stars
    stars = "★" * filled + "☆" * (max_stars - filled)

    html = f"""
    <div class="rank-row">
        {medal_html}
        <div class="rank-body">
            <div class="rank-title" title="{product.product}">{product.product}</div>
            <div class="rank-rating">
                <span class="rank-stars">{stars}</span>
                <span class="rank-score">{rating:.2f}</span>
            </div>
        </div>
    </div>
    """

    # Обёртка с классом для цветной полоски
    with st.container():
        st.markdown(html, unsafe_allow_html=True)


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

    left_col, right_col = st.columns([3, 1])

    with left_col:
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

    # --- Лучшее ---
    with right_col:
        st.subheader("Лучшие сегменты")
        ranked = vm.get_ranked_products("best")[:3]

        if not ranked:
            st.info("Нет данных")
        else:
            for i, p in enumerate(ranked, start=1):
                render_rank_card(i, p, p.avg_rating, "best")

        st.divider()

        # --- Худшее ---
        st.subheader("Проблемные сегменты")
        ranked_worst = vm.get_ranked_products("worst")[:3]

        if not ranked_worst:
            st.info("Нет данных")
        else:
            for i, p in enumerate(ranked_worst, start=1):
                render_rank_card(i, p, p.avg_rating, "worst")


