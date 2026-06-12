from pathlib import Path

import streamlit as st

from viewmodels.landing_vm import MANUAL_INPUT, LandingViewModel

def render_landing(vm: LandingViewModel):
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

    col1, col2 = st.columns(2)

    with col1:
        brand_selected = st.selectbox(
            "Бренд",
            options=vm.get_brand_options(),
            index=None,
            placeholder="Выберите бренд...",
            key="landing_brand",
        )
        if brand_selected == MANUAL_INPUT:
            brand_value = st.text_input(
                "Введите название бренда",
                placeholder="Vivienne Sabo",
                key="landing_brand_manual",
            )
        else:
            brand_value = brand_selected

        vm.set_brand(str(brand_value))

    with col2:
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

    col3, col4 = st.columns(2)

    with col3:
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


    with col4:
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

    st.divider()

    st.markdown("### Бренды")
    brands = vm.manager.get_brands()

    if not brands:
        st.info("Нет загруженных датасетов. Загрузите первый через форму выше.")
    else:
        cols = st.columns(3)
        for idx, brand_stats in enumerate(brands):
            with cols[idx % 3]:
                with st.container(border=True, height="stretch"):
                    st.subheader(brand_stats.brand)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.text(f"Датасетов: {brand_stats.datasets_count}")
                        st.text(f"Категорий: {brand_stats.categories_count}")
                    with c2:
                        st.text(f"Продуктов: {brand_stats.products_count}")
                        st.text(f"Отзывов: {brand_stats.reviews_count}")
                    st.button(
                        "🔍 Подробнее",
                        key=f"brand_{brand_stats.brand}",
                        use_container_width=True,
                        on_click=vm.on_brand_click,
                        args=(brand_stats.brand,)
                    )