from pathlib import Path

import streamlit as st

from app.services.dataset_manager import DatasetManager

DATASETS_DIR = Path("data/datasets")
MANUAL_INPUT = "+ Ввести вручную"


def on_brand_click(brand_name: str):
    st.session_state.selected_brand = brand_name
    st.session_state.page = "brand_page"


def on_upload_click():
    manager = DatasetManager(DATASETS_DIR)

    brand_value = st.session_state.get("landing_brand_value", "").strip()
    category_value = st.session_state.get("landing_category_value", "").strip()
    product_value = st.session_state.get("landing_product_value", "").strip()
    source_value = st.session_state.get("landing_source_value", "unknown").strip() or "unknown"
    uploaded_file = st.session_state.get("landing_uploaded_file")

    if not brand_value or not category_value or not product_value:
        st.session_state.landing_error = "Заполните все поля: бренд, категорию и продукт"
        return

    if uploaded_file is None:
        st.session_state.landing_error = "Загрузите JSON-файл с отзывами"
        return

    tmp_path = DATASETS_DIR / f"tmp_{uploaded_file.name}"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        meta = manager.upload_dataset(
            reviews_file=tmp_path,
            brand=brand_value,
            category=category_value,
            product=product_value,
            source=source_value,
        )

        st.session_state.selected_brand = meta.brand
        st.session_state.selected_product = meta.product
        st.session_state.page = "dashboard"
        st.session_state.dashboard_tab = "📊 Дашборд"
        st.session_state.landing_success = (
            f"✅ Загружен: {meta.brand} → {meta.product} ({meta.reviews_count} отзывов)"
        )
        st.session_state.landing_error = None

    except Exception as e:
        st.session_state.landing_error = f"❌ Ошибка загрузки: {e}"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def render_landing():
    css_file = Path(__file__).parent / "landing.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    manager = DatasetManager(DATASETS_DIR)
    all_datasets = manager.list_datasets()
    all_brands = sorted(set(ds.brand for ds in all_datasets))
    all_categories = sorted(set(ds.category for ds in all_datasets))
    all_products = sorted(set(ds.product for ds in all_datasets))
    all_sources = sorted(set(ds.source for ds in all_datasets))

    st.markdown('<h1 class="main-title">Reviews Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Анализ датасетов отзывов</p>', unsafe_allow_html=True)

    if msg := st.session_state.get("landing_error"):
        st.error(msg)
    if msg := st.session_state.get("landing_success"):
        st.success(msg)

    col1, col2 = st.columns(2)

    with col1:
        brand_options = all_brands + [MANUAL_INPUT]
        brand_selected = st.selectbox(
            "Бренд",
            options=brand_options,
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
            brand_value = brand_selected or ""

        st.session_state.landing_brand_value = brand_value

    with col2:
        category_options = all_categories + [MANUAL_INPUT]
        category_selected = st.selectbox(
            "Категория",
            options=category_options,
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

        st.session_state.landing_category_value = category_value

    col3, col4 = st.columns(2)

    with col3:
        if brand_value and category_value:
            filtered_products = sorted(
                {
                    ds.product
                    for ds in all_datasets
                    if ds.brand.strip().lower() == brand_value.strip().lower()
                    and ds.category.strip().lower() == category_value.strip().lower()
                }
            )
            product_options = filtered_products + [MANUAL_INPUT] if filtered_products else [MANUAL_INPUT]
        else:
            product_options = [MANUAL_INPUT]

        product_selected = st.selectbox(
            "Продукт",
            options=product_options,
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

        st.session_state.landing_product_value = product_value

    with col4:
        source_options = all_sources + [MANUAL_INPUT]
        source_selected = st.selectbox(
            "Источник",
            options=source_options,
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
            source_value = source_selected or "unknown"

        st.session_state.landing_source_value = source_value

    uploaded_file = st.file_uploader(
        "Загрузите JSON-файл с отзывами",
        type=["json"],
        key="landing_uploaded_file",
        help=(
            "Формат: массив отзывов\n"
            "[\n"
            '  {"review_id": 1, "author": "...", "date": "2026-05-03",\n'
            '   "title": "...", "rating": 5, "text": "...",\n'
            '   "pros": [...], "cons": [...]}\n'
            "]"
        ),
    )

    is_valid = bool(
        brand_value and category_value and product_value and source_value and uploaded_file is not None
    )

    st.button(
        "Загрузить и перейти к дашборду",
        type="primary",
        use_container_width=True,
        disabled=not is_valid,
        on_click=on_upload_click,
    )

    st.divider()

    st.markdown("### Бренды")
    brands = manager.get_brands()

    if not brands:
        st.info("Нет загруженных датасетов. Загрузите первый через форму выше.")
    else:
        cols = st.columns(3)
        for idx, brand_stats in enumerate(brands):
            with cols[idx % 3]:
                with st.container(border=True):
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
                        on_click=on_brand_click,
                        args=(brand_stats.brand,),
                    )