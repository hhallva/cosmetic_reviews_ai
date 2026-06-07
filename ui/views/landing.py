import streamlit as st
from pathlib import Path

from app.services.analytics import AnalyticsService
from app.services.dataset_manager import DatasetManager

DATASETS_DIR = Path("data/datasets")

def render_landing():
    """Главная страница: загрузка датасета или выбор из существующих."""
    css_file = Path(__file__).parent / "landing.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    manager = DatasetManager(DATASETS_DIR)

    st.markdown('<div class="landing-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">VS Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Анализ датасетов отзывов</p>', unsafe_allow_html=True)

    tab_upload, tab_select = st.tabs(["📤 Загрузить датасет", "📋 Выбрать из загруженных"])

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Загрузите JSON-файл датасета",
            type=["json"],
            help="Формат: {source, product, brand, reviews: [...]}",
        )
        if uploaded_file:
            # Сохраняем во временный файл
            tmp_path = DATASETS_DIR / f"tmp_{uploaded_file.name}"
            tmp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(tmp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                meta = manager.upload_dataset(tmp_path, skip_duplicate=True)
                st.success(f"✅ Загружен: **{meta.brand}** — {meta.product} ({meta.reviews_count} отзывов)")

                if st.button("🚀 Перейти к анализу", type="primary", use_container_width=True):
                    _go_to_dashboard(manager, [meta.id])
            except Exception as e:
                st.error(f"❌ Ошибка загрузки: {e}")
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

    with tab_select:
        existing = manager.list_datasets()
        if not existing:
            st.info("Нет загруженных датасетов. Загрузите первый через вкладку выше.")
        else:
            st.markdown(f"**Доступно датасетов:** {len(existing)}")

            # Группировка по продукту
            products = {}
            for m in existing:
                key = f"{m.brand} — {m.product}"
                if key not in products:
                    products[key] = []
                products[key].append(m)

            selected_options = st.multiselect(
                "Выберите один или несколько датасетов:",
                options=list(products.keys()),
                help="Можно выбрать несколько для сравнительного анализа",
            )

            if selected_options:
                # Собираем все ID выбранных продуктов
                selected_ids = []
                for opt in selected_options:
                    for m in products[opt]:
                        selected_ids.append(m.id)

                st.markdown(f"**Выбрано датасетов:** {len(selected_ids)}")

                # Показываем сводку
                for opt in selected_options:
                    metas = products[opt]
                    total_reviews = sum(m.reviews_count for m in metas)
                    st.caption(f"• {opt} ({len(metas)} датасет(ов), {total_reviews} отзывов)")

                if st.button("🚀 Анализировать выбранные", type="primary", use_container_width=True):
                    _go_to_dashboard(manager, selected_ids)

            st.divider()

            # Кнопка удаления
            st.markdown("**⚠️ Управление датасетами:**")
            delete_id = st.selectbox(
                "Удалить датасет:",
                options=[""] + [f"[{m.id}] {m.brand} — {m.product}" for m in existing],
                format_func=lambda x: x if x else "— Не выбрано —",
            )
            if delete_id and st.button(" Удалить", type="secondary"):
                ds_id = delete_id.split("]")[0].strip("[")
                if manager.delete_dataset(ds_id):
                    st.success("Удалено!")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def _go_to_dashboard(manager: DatasetManager, dataset_ids: list[str]):
    """Загружает датасеты, считает аналитику, сохраняет в session_state и переходит на дашборд."""
    datasets = manager.get_multiple(dataset_ids)
    if not datasets:
        st.error("Не удалось загрузить выбранные датасеты.")
        return

    analytics = AnalyticsService(datasets)
    dashboard_data = analytics.get_full_dashboard()

    # Сохраняем в session_state
    st.session_state.selected_datasets = datasets
    st.session_state.dashboard_data = dashboard_data
    st.session_state.all_reviews = analytics.all_reviews
    st.session_state.page = "dashboard"
    st.session_state.dashboard_tab = "Дашборд"
    st.rerun()
