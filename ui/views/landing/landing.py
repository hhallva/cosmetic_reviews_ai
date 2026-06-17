from pathlib import Path

import streamlit as st

from viewmodels.landing_vm import MANUAL_INPUT, LandingViewModel



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

def render_landing(vm: LandingViewModel):

    def render_product_card(product_stats, idx: int):
        stars = "⭐" * int(round(product_stats.avg_rating)) + "☆" * (5 - int(round(product_stats.avg_rating)))

        max_stars = 5
        filled = round(product_stats.avg_rating) if product_stats.avg_rating <= max_stars else max_stars
        stars = "★" * filled + "☆" * (max_stars - filled)
        with st.container(border=True):
            st.subheader(product_stats.product)
            c1, c2 = st.columns(2)
            with c1:
                st.text(product_stats.category)
                st.markdown(f"""
                    <div class="rank-rating">
                        <span class="rank-stars">{stars}</span>
                        <span class="rank-score">{product_stats.avg_rating:.2f}</span>
                    </div>""", unsafe_allow_html=True)
            with c2:
                st.text(f"Датасетов: {product_stats.datasets_count}")
                st.text(f"Отзывов: {product_stats.reviews_count}")

            st.button(
                "Подробнее",
                key=f"landing_product_{product_stats.product}_{idx}",
                use_container_width=True,
                on_click=lambda p=product_stats.product: vm.go_to_dashboard(p),
            )

    css_file = Path(__file__).parent / "landing.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Reviews Analytics</h1>', text_alignment="center", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Анализ датасетов отзывов</p>', text_alignment="center", unsafe_allow_html=True)

    if vm.error:
        st.error(vm.error)
    if vm.success:
        st.success(vm.success)

    col1, col2, col3= st.columns(3)

    with col1:
        category_selected = st.selectbox(
            "Категория",
            options=vm.get_category_options(),
            index=None,
            placeholder="Выберите категорию...",
            key="landing_category",
        )

        if category_selected == MANUAL_INPUT:
            category_value = st.text_input(
                "Введите название категории",
                placeholder="Декоративная косметика",
                key="landing_category_manual",
            )
        else:
            category_value = category_selected or ""

        vm.set_category(str(category_value))
    with col2:
        product_selected = st.selectbox(
            "Продукт",
            options=vm.get_product_options(),
            index=None,
            placeholder="Выберите продукт...",
            key="landing_product",
        )
        if product_selected == MANUAL_INPUT:
            product_value = st.text_input(
                "Введите название продукта",
                placeholder="Cabaret Premiere",
                key="landing_product_manual",
            )
        else:
            product_value = product_selected or ""

        vm.set_product(str(product_value))
    with col3:
        source_selected = st.selectbox(
            "Источник",
            options=vm.get_source_options(),
            index=None,
            placeholder="Выберите источник...",
            key="landing_source",
        )

        if source_selected == MANUAL_INPUT:
            source_value = st.text_input(
                "Введите название источника",
                placeholder="Например: iRecommend",
                key="landing_source_manual",
            )
        else:
            source_value = source_selected or ""

        vm.set_source(str(source_value))

    uploaded_file = st.file_uploader(
        "Загрузите JSON-файл с отзывами",
        type=["json"],
        key="landing_uploaded_file",
    )
    vm.set_uploaded_file(uploaded_file)

    st.button(
        "Загрузить и перейти к дашборду",
        type="primary",
        use_container_width=True,
        disabled=not vm.can_upload(),
        on_click=vm.upload,
    )

    st.markdown("### Продукты")

    left, right = st.columns([3, 1])

    with left:
        products = vm.manager.get_products_by_brand(vm.fixed_brand)

        if not products:
            st.info("Нет загруженных продуктов.")
        else:
            cols = st.columns(3)
            for idx, product_stats in enumerate(products):
                with cols[idx % 3]:
                    render_product_card(product_stats, idx)

    with right:
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