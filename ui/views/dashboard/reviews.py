import streamlit as st

def render_reviews_view(reviews_list: list, product_name: str):
    st.header(f"📝 Просмотр отзывов: {product_name}")
    st.divider()
    st.markdown(f"**Всего отображено отзывов: {len(reviews_list)}**")
    st.markdown("<br>", unsafe_allow_html=True)

    for rev in reviews_list:
        stars = "⭐" * rev["rating"] + "☆" * (5 - rev["rating"])
        st.markdown(f"""
        <div class="review-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div>
                    <strong>👤 {rev['author']}</strong> 
                    <span style="color: #6c757d; font-size: 0.85rem; margin-left: 10px;">{rev['date']}</span>
                </div>
                <span>{stars}</span>
            </div>
            <div style="color: #495057; font-size: 0.95rem; line-height: 1.5;">"{rev['text']}"</div>
        </div>
        """, unsafe_allow_html=True)