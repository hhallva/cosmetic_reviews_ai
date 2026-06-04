import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def render_metrics_view(metrics: dict, segments_df, trends_df, ai_text: str, product_name: str):
    st.header(f"📊 Дашборд: {product_name}")
    st.divider()

    # KPI Блок
    st.markdown('<div class="section-header">Ключевые показатели (KPI)</div>', unsafe_allow_html=True)
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1: st.metric("📝 Всего отзывов", f"{metrics['total_reviews']}", delta="+12%")
    with kpi2: st.metric("⚖️ Sentiment Score", f"{metrics['sentiment_score']}%")
    with kpi3: st.metric("😊 Позитивные", f"{metrics['pos_pct']}%")
    with kpi4: st.metric("😡 Негативные", f"{metrics['neg_pct']}%", delta_color="inverse")
    with kpi5: st.metric("⭐ Средний рейтинг", f"{metrics['avg_rating']}/5.0")
    with kpi6: st.metric("🔥 Demand Index", f"{metrics['demand_index']}/100")

    st.markdown("<br>", unsafe_allow_html=True)

    # Графики сегментов
    st.markdown('<div class="section-header">Аналитика по сегментам</div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Позитивные', 'Нейтральные', 'Негативные'],
            values=[metrics['pos_pct'], 100 - metrics['pos_pct'] - metrics['neg_pct'], metrics['neg_pct']],
            hole=0.4, marker_colors=['#28a745', '#6c757d', '#dc3545']
        )])
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        fig_bar = px.bar(segments_df, x="Линейка", y="Sentiment Score", color="Цвет",
                         color_discrete_map="identity", text="Sentiment Score")
        fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=False,
                              yaxis=dict(range=[-20, 100]))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Динамика и спрос
    st.markdown('<div class="section-header">Динамика и Индекс спроса</div>', unsafe_allow_html=True)
    trend_col, demand_col = st.columns([2, 1])

    with trend_col:
        fig_line = px.line(trends_df, x="Месяц", y=["Позитивные", "Негативные"], markers=True,
                           color_discrete_map={"Позитивные": "#28a745", "Негативные": "#dc3545"})
        fig_line.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_line, use_container_width=True)

    with demand_col:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=metrics['demand_index'], domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Demand Index"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#d63384"},
                   'steps': [{'range': [0, 40], 'color': "#f8d7da"},
                             {'range': [40, 70], 'color': "#fff3cd"},
                             {'range': [70, 100], 'color': "#d4edda"}]}
        ))
        fig_gauge.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()
    st.markdown('<div class="section-header">🤖 ИИ-Вывод и рекомендации</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-block">{ai_text}</div>', unsafe_allow_html=True)