# app/ui/views/dashboard/metrics.py
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from app.services.kpi.ai_analyzer import analyze_with_Yandex


def render_metrics_view(data: dict, all_reviews: dict):
    css_file = Path(__file__).parent / "metrics.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with st.container(border=True):
        kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7 = st.columns(7)

        with kpi1:
            st.metric("Всего отзывов", data["total_reviews"])
        with kpi2:
            sentiment_score = data["sentiment_score"]
            value_str = f"{sentiment_score:+.1f}%" if sentiment_score < 0 else f"{sentiment_score:-.1f}%"
            st.metric(
                label="Sentiment Score",
                value=value_str,
            )
        with kpi3:
            sent_dist = data["sentiment_dist"]
            st.metric("Позитивные", f"{sent_dist['positive_pct']}%")
        with kpi4:
            st.metric("Негативные", f"{sent_dist['negative_pct']}%", delta_color="inverse")
        with kpi5:
            st.metric("Средний рейтинг", f"{data['avg_rating']}/5.0")
        with kpi6:
            st.metric("Индекс жалоб", f"{data['problems_index']}")
        with kpi7:
            st.metric("Индекс спроса", f"{data['demand_index']}")

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
        ratings = [r.rating for r in all_reviews if r.rating is not None]
        rating_dist = {i: ratings.count(i) for i in range(1, 6)}
        fig_bar = go.Figure(data=[go.Bar(
            x=[str(i) for i in range(1, 6)],
            y=[rating_dist.get(i, 0) for i in range(1, 6)],
            marker_color=["#dc3545", "#fd7e14", "#ffc107", "#20c997", "#28a745"],
            text=[rating_dist.get(i, 0) for i in range(1, 6)],
            textposition="outside",
        )])
        fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_bar, use_container_width=True)

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
                st.markdown("### Ключевые боли")
                pain_points = analysis.get("pain_points", [])

                if not pain_points:
                    st.caption("Боли не выявлены")
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

