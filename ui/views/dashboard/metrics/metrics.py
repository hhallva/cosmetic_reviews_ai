# app/ui/views/dashboard/metrics.py
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def render_metrics_view(data: dict, all_reviews: dict):
    css_file = Path(__file__).parent / "metrics.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.header("Аналитика датасетов")
    st.divider()

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6= st.columns(6)

    with kpi1:
        st.metric("Всего отзывов", data["total_reviews"])
    with kpi2:
        sentiment_score = data["sentiment_score"]
        delta = f"{sentiment_score:+.1f}%" if sentiment_score != 0 else "0%"
        st.metric("Sentiment Score", f"{sentiment_score:+.1f}%", delta=delta)
    with kpi3:
        sent_dist = data["sentiment_dist"]
        st.metric("Позитивные", f"{sent_dist['positive_pct']}%")
    with kpi4:
        st.metric("Негативные", f"{sent_dist['negative_pct']}%", delta_color="inverse")
    with kpi5:
        st.metric("Средний рейтинг", f"{data['avg_rating']}/5.0")
    with kpi6:
        st.metric("Индекс жалоб", f"{data['problems_index']}")


    st.markdown('<div class="section-header">Распределение отзывов по тональности</div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        sent_dist = data["sentiment_dist"]
        labels = ["Позитивные", "Нейтральные", "Негативные"]
        values = [sent_dist["positive"], sent_dist["neutral"], sent_dist["negative"]]
        colors = ["#28a745", "#6c757d", "#dc3545"]
        fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, marker_colors=colors, textinfo="label+percent")])
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        ratings = [r.rating for r in all_reviews if r.rating is not None]
        rating_dist = {i: ratings.count(i) for i in range(1, 6)}
        fig_bar = go.Figure(data=[go.Bar(
            x=[str(i) for i in range(1, 6)],
            y=[rating_dist.get(i, 0) for i in range(1, 6)],
            marker_color=["#dc3545", "#fd7e14", "#ffc107", "#20c997", "#28a745"],
            text=[rating_dist.get(i, 0) for i in range(1, 6)],
            textposition="outside",
        )])
        fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, title="Распределение рейтингов")
        st.plotly_chart(fig_bar, use_container_width=True)

    if data["reviews_over_time"]:
        st.markdown('<div class="section-header">Динамика отзывов по времени</div>', unsafe_allow_html=True)
        df_time = pd.DataFrame(data["reviews_over_time"])
        df_time["month"] = pd.to_datetime(df_time["month"])
        fig_line = px.line(df_time, x="month", y="count", markers=True, title="Количество отзывов по месяцам")
        fig_line.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_line, use_container_width=True)