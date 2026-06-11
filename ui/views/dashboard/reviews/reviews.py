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

    st.markdown(f"Показано отзывов: **{len(filtered)}** из {len(reviews_list)}")
    st.divider()

    for rev in filtered:
        stars = "⭐" * (rev.rating or 0) + "☆" * (5 - (rev.rating or 0))
        rating_label = f"{rev.rating}/5" if rev.rating else "Без оценки"
        pros_str = ", ".join(rev.pros) if rev.pros else "нет"
        cons_str = ", ".join(rev.cons) if rev.cons else "нет"

        with st.container(border=True):
            st.markdown(
                f"""
                        <div class="review-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <div>
                                    <strong>👤 {rev.author}</strong>
                                    <span style="color:#6c757d; font-size:0.85rem; margin-left:10px;">{rev.date}</span>
                                </div>
                                <span>{stars} <small>({rating_label})</small></span>
                            </div>
                            <div style="font-weight:bold; margin-bottom:6px;">{rev.title}</div>
                            <div font-size:0.95rem; line-height:1.5; margin-bottom:10px;">
                                {rev.text}
                            </div>
                            <div style="font-size:0.85rem;">
                                <span style="color:#28a745;">✅ {pros_str}</span><br>
                                <span style="color:#dc3545;">❌ {cons_str}</span>
                            </div>
                        </div>
                        """,
                unsafe_allow_html=True,
            )






