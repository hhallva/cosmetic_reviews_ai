import time

import streamlit as st
import app.core.constants as consts
from app.services.search.search_manager import SearchManager
from app.services.storage.json_storage import JSONStorage

st.set_page_config(
    page_title="Vivienne Sabo Review Analyzer",
    page_icon="💄",
    layout="wide"
)

st.title("Vivienne Sabo")

# Собираем все варианты в один список
all_options = [
    f"{line} {product}"
    for line, products in consts.PRODUCTS.items()
    for product in products
]

# Разбиваем на колонки для компактности
col_input, col_btn, col_empty = st.columns([4, 1, 5])

with col_input:
    selected_value = st.selectbox(
        label="Поиск",
        options=all_options,
        index=None, # Начинаем с пустого поля
        placeholder="Выберите товар"
    )

    final_product = selected_value

with col_btn:
    st.markdown(
        """<div style="display: flex; align-items: flex-end; height: 100%; padding-top: 28px;">""",
        unsafe_allow_html=True
    )
    search_clicked = st.button("Найти", type="primary", use_container_width=True)


# Логика срабатывает по нажатию кнопки
if search_clicked:
    if not final_product:
        st.error("Сначала выберите товар из списка.")
    else:
        progress_bar = st.progress(0, "")

        try:
            # 1. Инициализация и поиск
            progress_bar.progress(10, "Инициализация менеджера поиска...")
            time.sleep(0.3)

            progress_bar.progress(30, "Сканирование источников и сбор отзывов...")

            manager = SearchManager()
            results = manager.search(
                product_name=final_product,
                max_results=5
            )

            progress_bar.progress(70, "Сохранение результатов в JSON...")

            storage = JSONStorage()
            storage.save_search_results(
                product_name=final_product,
                results=results
            )

            # Шаг 4: Завершение
            progress_bar.progress(100, "Готово!")
            time.sleep(0.5)

            # Убираем прогресс-бар после завершения, чтобы не мусорить в интерфейсе
            progress_bar.empty()

            if not results:
                st.warning(f"Отзывы для '{final_product}' не найдены.")
            else:
                st.success(f"Найдено и сохранено: {len(results)} отзывов")
                st.subheader("Результаты поиска:")
                for i, review in enumerate(results, 1):
                    with st.expander(f"Отзыв #{i}", expanded=(i == 1)):
                        st.write(review)

        except Exception as e:
            st.error(f"Произошла ошибка при поиске: {e}")
