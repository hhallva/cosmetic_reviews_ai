# app/ui/views/dashboard/metrics.py
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from app.services.ai_analyzer import analyze_with_Yandex


def render_metrics_view(data: dict, all_reviews: dict):
    css_file = Path(__file__).parent / "metrics.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    demand_index = data['demand_index']
    if demand_index >= 70:
        color = "#28a745"
        level = "Высокий"
    elif demand_index >= 40:
        color = "#ffc107"
        level = "Средний"
    else:
        color = "#dc3545"
        level = "Низкий"

    st.markdown(f"""
                <div style='text-align: center; padding: 5px'>
                    <div style='font-size: 14px; font-weight: 500; margin-bottom: 10px;'>Индекс спроса</div>
                    <div style='position: relative; width: 100%; background: #b1b9c1; border-radius: 20px; height: 30px; overflow: hidden;'>
                        <div style='position: absolute; left: 0; top: 0; width: {demand_index}%; background: {color}; height: 100%; transition: width 0.3s ease;'></div>
                        <div style='position: relative; line-height: 30px; color: {'white' if demand_index > 50 else 'black'}; font-weight: 600; z-index: 1;'>
                            {demand_index}% — {level}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with st.container(border=True):
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

        with kpi1:
            st.metric("Всего отзывов", data["total_reviews"])
        with kpi2:
            sent_dist = data["sentiment_dist"]
            st.metric("Позитивные", f"{sent_dist['positive_pct']}%")
        with kpi3:
            st.metric("Негативные", f"{sent_dist['negative_pct']}%")
        with kpi4:
            # Используем средний сентимент вместо звездного рейтинга
            avg_sentiment = data.get("avg_sentiment", 0.0)
            st.metric("Средний сентимент", f"{avg_sentiment:.2f}")
        with kpi5:
            st.metric("Индекс жалоб", f"{data['problems_index']}")



    chart_col1, chart_col2 = st.columns(2, vertical_alignment="center")

    with chart_col1:
        st.text("Распределение отзывов по тональности")
        sent_dist = data["sentiment_dist"]
        labels = ["Позитивные", "Нейтральные", "Негативные"]
        values = [sent_dist["positive"], sent_dist["neutral"], sent_dist["negative"]]
        colors = ["#28a745", "#6c757d", "#dc3545"]
        fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, marker_colors=colors, textinfo="label+percent")])
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        st.text("Индекс тональности")
        sentiment_score = data["sentiment_score"]

        # Создаем gauge chart такого же размера как пончик
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment_score,
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [-100, 100], "tickwidth": 1, "tickcolor": "darkgray",
                         "tickvals": [-100, -50, 0, 50, 100]},
                "bar": {"color": "white"},
                "steps": [
                    {"range": [-100, -60], "color": "#8B0000"},
                    {"range": [-60, -20], "color": "#DC143C"},
                    {"range": [-20, 0], "color": "#FF6B6B"},
                    {"range": [0, 20], "color": "#90EE90"},
                    {"range": [20, 60], "color": "#32CD32"},
                    {"range": [60, 100], "color": "#006400"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 2},
                    "thickness": 0.75,
                    "value": sentiment_score,
                },
            },
            number={
                "suffix": "%",
                "font": {"size": 28, "color": "#FF4B4B" if sentiment_score < 0 else "#4CAF50"}
            },
        ))

        fig_gauge.update_layout(
            height=300,  # Такая же высота как у пончика
            margin=dict(t=40, b=20, l=20, r=20)
        )

        st.plotly_chart(fig_gauge, use_container_width=True)

    if data["reviews_over_time"]:
        st.text("Количество отзывов по месяцам")
        df_time = pd.DataFrame(data["reviews_over_time"])
        df_time["month"] = pd.to_datetime(df_time["month"])
        fig_line = px.line(df_time, x="month", y="count", markers=True)
        fig_line.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_line, use_container_width=True)

    def _render_ai_analysis(analysis: dict):
        """Отрисовка результатов ИИ-анализа."""

        st.markdown("## ИИ-анализ и рекомендации")

        executive_summary = analysis.get("executive_summary", "")
        if executive_summary:
            st.info(executive_summary)

        themes = analysis.get("themes", [])
        if themes:
            chips = " ".join([f"`{t}`" for t in themes])
            st.markdown(chips)

        col_left, col_right = st.columns(2)

        with col_left:
            with st.container(border=True):
                st.markdown("### Слабые стороны")
                pain_points = analysis.get("pain_points", [])

                if not pain_points:
                    st.caption("Слабых сторон не выявлено")
                else:
                    for pain in pain_points:
                        frequency = (pain.get("frequency", "") or "").lower()
                        icon = {"высокая": "🔴", "средняя": "🟡", "низкая": "🟢"}.get(frequency, "⚪")

                        text = {"высокая": "Высокий", "средняя": "Средний", "низкая": "Низкий"}.get(frequency,"без приоритета")

                        title = f"{pain.get('category', 'Неизвестно').capitalize()} | {icon} {text}"
                        with st.expander(title):
                            examples = pain.get("examples", [])
                            if examples:
                                for ex in examples:
                                    st.text(ex)
                            else:
                                st.caption("Примеры отсутствуют")

        with col_right:
            with st.container(border=True):
                st.markdown("### Сильные стороны")
                strengths = analysis.get("strengths", [])

                if not strengths:
                    st.caption("Сильные стороны не выявлены")
                else:
                    for strength in strengths:
                        frequency = (pain.get("frequency", "") or "").lower()
                        icon = {"высокая": "🔴", "средняя": "🟡", "низкая": "🟢"}.get(frequency, "⚪")

                        text = {"высокая": "Высокий", "средняя": "Средний", "низкая": "Низкий"}.get(frequency,"без приоритета")

                        title = f"{strength.get('category', 'Неизвестно').capitalize()} | {icon} {text}"
                        with st.expander(title):
                            examples = strength.get("examples", [])
                            if examples:
                                for ex in examples:
                                    st.text(ex)
                            else:
                                st.caption("Примеры отсутствуют")

        recommendations = analysis.get("recommendations", [])
        with st.container(border=True):
            st.markdown("### Рекомендации")

            if not recommendations:
                st.caption("Рекомендаций нет")
            else:
                for rec in recommendations:
                    priority = (rec.get("priority", "") or "").lower()
                    icon = {"высокая": "🔴", "средняя": "🟡", "низкая": "🟢"}.get(priority, "⚪")
                    text = {"высокая": "Высокий", "средняя": "Средний", "низкая": "Низкий"}.get(priority, "без приоритета")

                    st.markdown(
                        f"""
                            {icon} **{text} приоритет**  
                            **Действие:** {rec.get('action', '—')}  
                            **Ожидаемый эффект:** {rec.get('expected_impact', '—')}
                            """
                    )



    # === ИИ-АНАЛИЗ ===
    st.divider()

    # Кнопки управления
    run_analysis = st.button("Запустить ИИ-анализ", type="primary")

    # Запуск анализа
    if run_analysis:
        with st.spinner("Анализируем отзывы и KPI через YandexGPT... Это может занять 10-30 секунд."):
            # ✅ all_reviews — это список Pydantic-объектов Review,
            # внутри analyze_with_Yandex они автоматически конвертируются в dict
            analysis = analyze_with_Yandex(data, all_reviews)

            if analysis:
                st.session_state["ai_analysis"] = analysis
                st.success("✅ Анализ завершён!")
                st.rerun()  # Перерисовываем, чтобы показать результат
            else:
                st.error("❌ Не удалось получить анализ. Проверьте логи и настройки API.")

    # Отображение сохранённого результата (сохраняется между rerun)
    analysis = st.session_state.get("ai_analysis")
    if analysis:
        _render_ai_analysis(analysis)

