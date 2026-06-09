import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render_metrics_view(data: dict):
    """Рендерит дашборд из данных AnalyticsService с новыми KPI."""

    st.header("Аналитика датасетов")
    st.divider()

    # --- 1. KPI БЛОК (8 метрик) ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

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
        st.metric("️Индекс жалоб", f"{data['problems_index']}")

    with kpi7:
        best = data["best_segment"]
        st.metric("Лучший сегмент", f"{best['product']}", delta=f"{best['avg_rating']}/5.0")

    with kpi8:
        worst = data["worst_segment"]
        st.metric("Проблемный сегмент", f"{worst['product']}", delta=f"{worst['avg_rating']}/5.0",
                  delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 2. РАСПРЕДЕЛЕНИЕ ТОНАЛЬНОСТИ ---
    st.markdown('<div class="section-header">Распределение отзывов по тональности</div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Donut chart
        sent_dist = data["sentiment_dist"]
        labels = ['Позитивные', 'Нейтральные', 'Негативные']
        values = [sent_dist['positive'], sent_dist['neutral'], sent_dist['negative']]
        colors = ['#28a745', '#6c757d', '#dc3545']

        fig_donut = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo="label+percent",
        )])
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, title="Sentiment Distribution")
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        # Bar chart рейтингов
        all_reviews = []
        for ds in st.session_state.selected_datasets:
            all_reviews.extend(ds.reviews)

        ratings = [r.rating for r in all_reviews if r.rating is not None]
        rating_dist = {i: ratings.count(i) for i in range(1, 6)}

        fig_bar = go.Figure(data=[go.Bar(
            x=[str(i) for i in range(1, 6)],
            y=[rating_dist.get(i, 0) for i in range(1, 6)],
            marker_color=['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#28a745'],
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

    # --- 3. ДИНАМИКА ОТЗЫВОВ ---
    if data["reviews_over_time"]:
        st.markdown('<div class="section-header">Динамика отзывов по времени</div>', unsafe_allow_html=True)

        df_time = pd.DataFrame(data["reviews_over_time"])
        df_time["month"] = pd.to_datetime(df_time["month"])

        fig_line = px.line(df_time, x="month", y="count", markers=True, title="Количество отзывов по месяцам")
        fig_line.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # --- 4. ИНДЕКС СПРОСА (Gauge) ---
    st.markdown('<div class="section-header">Индекс потенциального спроса (Demand Index)</div>', unsafe_allow_html=True)

    demand_col1, demand_col2 = st.columns([1, 2])

    with demand_col1:
        demand_index = data["demand_index"]
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=demand_index,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Demand Index"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#d63384"},
                'steps': [
                    {'range': [0, 40], 'color': "#f8d7da"},
                    {'range': [40, 70], 'color': "#fff3cd"},
                    {'range': [70, 100], 'color': "#d4edda"}
                ]
            }
        ))
        fig_gauge.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with demand_col2:
        st.markdown("""
        **Интерпретация Demand Index:**
        - **0-40** — Низкий спрос (мало позитивных отзывов, падающая динамика)
        - **40-70** — Умеренный спрос (стабильная ситуация)
        - **70-100** — Высокий спрос (много позитива, растущая динамика)

        **Рекомендация:** Товары с высоким Demand Index стоит поддерживать и расширять их предложение.
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 5. ТОП ПРОС/КОНС ---
    st.markdown('<div class="section-header">Топ достоинств и недостатков</div>', unsafe_allow_html=True)

    pros_col, cons_col = st.columns(2)

    with pros_col:
        st.markdown("### 👍 Топ достоинств")
        if data["top_pros"]:
            df_pros = pd.DataFrame(data["top_pros"][:10])
            fig_pros = px.bar(df_pros, x="count", y="text", orientation="h", title="Топ-10 достоинств")
            fig_pros.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=400, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_pros, use_container_width=True)
        else:
            st.info("Нет данных о достоинствах")

    with cons_col:
        st.markdown("### 👎 Топ недостатков")
        if data["top_cons"]:
            df_cons = pd.DataFrame(data["top_cons"][:10])
            fig_cons = px.bar(df_cons, x="count", y="text", orientation="h", title="Топ-10 недостатков")
            fig_cons.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=400, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_cons, use_container_width=True)
        else:
            st.info("Нет данных о недостатках")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 6. ТОП СЛОВ ---
    if data["top_words"]:
        st.markdown('<div class="section-header">Топ слов в отзывах</div>', unsafe_allow_html=True)

        df_words = pd.DataFrame(data["top_words"][:15])
        fig_words = px.bar(df_words, x="count", y="word", orientation="h", title="Топ-15 слов")
        fig_words.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=400, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_words, use_container_width=True)