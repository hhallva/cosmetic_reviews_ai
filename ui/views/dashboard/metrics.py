import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def render_metrics_view(data: dict):
    """Рендерит дашборд из данных AnalyticsService."""
    summary = data["summary"]
    sentiment = data["sentiment"]
    top_pros = data["top_pros"]
    top_cons = data["top_cons"]
    top_words = data["top_words"]
    reviews_over_time = data["reviews_over_time"]

    st.header("📊 Аналитика датасетов")
    st.divider()

    # --- KPI ---
    st.markdown('<div class="section-header">Ключевые показатели</div>', unsafe_allow_html=True)
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.metric("📝 Всего отзывов", summary["total_reviews"])
    with kpi2:
        st.metric(" Датасетов", summary["datasets_count"])
    with kpi3:
        st.metric("⭐ Средний рейтинг", f"{summary['avg_rating']}/5.0")
    with kpi4:
        pos = sentiment["positive"]
        total_with_rating = sum(sentiment.values()) - sentiment["unknown"]
        pos_pct = round(pos / total_with_rating * 100, 1) if total_with_rating else 0
        st.metric("😊 Позитивные", f"{pos_pct}%")
    with kpi5:
        neg = sentiment["negative"]
        neg_pct = round(neg / total_with_rating * 100, 1) if total_with_rating else 0
        st.metric("😡 Негативные", f"{neg_pct}%", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ГРАФИКИ: Sentiment + Рейтинг ---
    st.markdown('<div class="section-header">Распределение</div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Pie chart sentiment
        labels = ["Позитивные", "Нейтральные", "Негативные", "Без оценки"]
        values = [sentiment["positive"], sentiment["neutral"], sentiment["negative"], sentiment["unknown"]]
        colors = ["#28a745", "#6c757d", "#dc3545", "#ffc107"]

        fig_donut = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo="label+percent",
        )])
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, title="Sentiment")
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        # Bar chart рейтингов
        rating_dist = summary["rating_distribution"]
        fig_bar = go.Figure(data=[go.Bar(
            x=[str(i) for i in range(1, 6)],
            y=[rating_dist.get(i, 0) for i in range(1, 6)],
            marker_color=["#dc3545", "#fd7e14", "#ffc107", "#20c997", "#28a745"],
            text=[rating_dist.get(i, 0) for i in range(1, 6)],
            textposition="outside",
        )])
        fig_bar.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=300,
            title="Распределение рейтингов",
            xaxis_title="Рейтинг",
            yaxis_title="Количество",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ДИНАМИКА ПО ВРЕМЕНИ ---
    if reviews_over_time:
        st.markdown('<div class="section-header">Динамика отзывов по времени</div>', unsafe_allow_html=True)
        df_time = px.data.tips()  # заглушка, ниже нормальный dataframe
        import pandas as pd
        df_time = pd.DataFrame(reviews_over_time)
        df_time["month"] = pd.to_datetime(df_time["month"])

        fig_line = px.line(df_time, x="month", y="count", markers=True, title="Количество отзывов по месяцам")
        fig_line.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # --- ТОП СЛОВ ---
    if top_words:
        st.markdown('<div class="section-header"> Топ слов в отзывах</div>', unsafe_allow_html=True)
        df_words = pd.DataFrame(top_words[:15])
        fig_words = px.bar(df_words, x="count", y="word", orientation="h", title="Топ-15 слов")
        fig_words.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=400, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_words, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # --- ТОП PROS / CONS ---
    pros_col, cons_col = st.columns(2)

    with pros_col:
        st.markdown('<div class="section-header"> Топ достоинств</div>', unsafe_allow_html=True)
        if top_pros:
            df_pros = pd.DataFrame(top_pros)
            for _, row in df_pros.iterrows():
                st.markdown(f"**{row['text'].title()}** — {row['count']} упоминаний")
        else:
            st.info("Нет данных о достоинствах")

    with cons_col:
        st.markdown('<div class="section-header">👎 Топ недостатков</div>', unsafe_allow_html=True)
        if top_cons:
            df_cons = pd.DataFrame(top_cons)
            for _, row in df_cons.iterrows():
                st.markdown(f"**{row['text'].title()}** — {row['count']} упоминаний")
        else:
            st.info("Нет данных о недостатках")