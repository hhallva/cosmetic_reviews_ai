# app/ui/views/dashboard/reviews.py
from pathlib import Path

import streamlit as st


def render_reviews_view(reviews_list: list):
    css_file = Path(__file__).parent / "reviews.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.header("📝 Отзывы")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        min_rating = st.slider("Минимальный рейтинг", 0, 5, 0)
    with col2:
        sentiment_filter = st.selectbox("Sentiment", ["Все", "Позитивные (4-5)", "Нейтральные (3)", "Негативные (1-2)"])
    with col3:
        search_text = st.text_input("🔍 Поиск по тексту")

    filtered = []
    for rev in reviews_list:
        if rev.rating is not None and rev.rating < min_rating:
            continue
        if sentiment_filter != "Все" and rev.rating is not None:
            if sentiment_filter == "Позитивные (4-5)" and rev.rating < 4:
                continue
            if sentiment_filter == "Нейтральные (3)" and rev.rating != 3:
                continue
            if sentiment_filter == "Негативные (1-2)" and rev.rating > 2:
                continue
        if search_text and search_text.lower() not in (rev.text or "").lower():
            continue
        filtered.append(rev)

    st.text(f"Показано отзывов: {len(filtered)} из {len(reviews_list)}")
    st.divider()

    for rev in filtered:
        stars = "⭐" * (rev.rating or 0)
        pros_str = ", ".join(rev.pros) if rev.pros else "нет"
        cons_str = ", ".join(rev.cons) if rev.cons else "нет"

        with st.container(border=True):
            col_author, col_stars = st.columns([3, 1])


            with col_author:
                st.text(f"{rev.author}      {rev.date}")
            with col_stars:
                st.text(f"{stars}", width="stretch", text_alignment="right")

            if rev.title:
                st.subheader(f"{rev.title}")
            st.text(rev.text)

            st.text(f"✅ Плюсы: {pros_str}")
            st.text(f"❌ Минусы: {cons_str}")







