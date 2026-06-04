import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
from datetime import datetime, timedelta
import app.core.constants as consts

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="Vivienne Sabo Analytics",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="collapsed"  # Скрыт по умолчанию для стартовой страницы
)

# --- CSS СТИЛИ ---
st.markdown("""
    <style>
    /* Скрываем сайдбар, когда мы не на странице дашборда */
    .hide-sidebar [data-testid="stSidebar"] { display: none !important; }
    .show-sidebar [data-testid="stSidebar"] { display: block !important; }

    .block-container { padding-top: 2rem; }
    .section-header { 
        font-size: 1.3rem; font-weight: 700; color: #212529; 
        margin-bottom: 1rem; border-bottom: 2px solid #d63384; padding-bottom: 0.5rem;
    }
    .review-card {
        background-color: #ffffff; border: 1px solid #e9ecef; border-left: 4px solid #d63384;
        border-radius: 6px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .source-card {
        background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px;
        padding: 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;
    }
    .ai-block {
        background: linear-gradient(135deg, #fff0f6 0%, #f8f9fa 100%);
        border-radius: 8px; padding: 20px; border: 1px solid #fcc2d7;
    }
    [data-theme="dark"] .review-card, [data-theme="dark"] .source-card { background-color: #262730; border-color: #4a4b57; }
    [data-theme="dark"] .ai-block { background: linear-gradient(135deg, #2c2e3a 0%, #1e1e24 100%); border-color: #4a4b57; }
    </style>
""", unsafe_allow_html=True)


# --- ФУНКЦИЯ ГЕНЕРАЦИИ ТЕСТОВЫХ ДАННЫХ ---
def generate_mock_data(product_name):
    total = random.randint(150, 1200)
    pos = random.randint(60, 80)
    neg = random.randint(10, 25)

    metrics = {
        "total_reviews": total, "sentiment_score": pos - neg, "pos_pct": pos,
        "neg_pct": neg, "avg_rating": round(random.uniform(3.8, 4.7), 1),
        "problems_index": round(random.uniform(0.1, 0.4), 2), "demand_index": round(random.uniform(65, 95), 1)
    }

    segments = pd.DataFrame({
        "Линейка": ["Cabaret", "Cinecitta", "Makeup Revolution", "Garden", "Rare"],
        "Sentiment Score": [75, 60, 45, 30, -15],
        "Цвет": ["#28a745", "#28a745", "#ffc107", "#ffc107", "#dc3545"]
    })

    dates = [(datetime.now() - timedelta(days=30 * i)).strftime("%b %Y") for i in range(5, -1, -1)]
    trends = pd.DataFrame({
        "Месяц": dates,
        "Позитивные": [random.randint(20, 50) + i * 5 for i in range(6)],
        "Негативные": [random.randint(5, 15) - i for i in range(6)]
    })

    sources = [
        {"name": "Wildberries", "url": "https://www.wildberries.ru", "count": random.randint(500, 2000)},
        {"name": "Ozon", "url": "https://www.ozon.ru", "count": random.randint(300, 1500)},
        {"name": "IRecommend", "url": "https://irecommend.ru", "count": random.randint(100, 800)},
    ]

    reviews = [
        {"author": "Анна К.", "rating": 5, "date": "12.05.2024", "text": "Лучшая тушь! Не осыпается весь день."},
        {"author": "Мария В.", "rating": 4, "date": "10.05.2024",
         "text": "Хорошая, но кисточка могла бы быть удобнее."},
        {"author": "Елена С.", "rating": 2, "date": "08.05.2024", "text": "Разочарована. Осыпалась через 3 часа."},
    ]

    ai_insights = f"""
    • **Общий тренд**: Продукт "{product_name}" демонстрирует устойчивый рост. Sentiment Score в зеленой зоне ({metrics['sentiment_score']}%).
    • **Зона риска**: Выявлен рост упоминаний проблемы "осыпание" в последних 15% отзывов.
    • **Рекомендация**: Индекс спроса ({metrics['demand_index']}/100) указывает на высокий потенциал. Рекомендуется усилить маркетинговую поддержку.
    """
    return metrics, segments, trends, sources, reviews, ai_insights


# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ (РОУТИНГ) ---
if "page" not in st.session_state:
    st.session_state.page = "landing"  # landing, reports_list, dashboard
if "dashboard_tab" not in st.session_state:
    st.session_state.dashboard_tab = "📊 Дашборд"
if "selected_product" not in st.session_state:
    st.session_state.selected_product = ""
if "report_data" not in st.session_state:
    st.session_state.report_data = None

# Список всех товаров для комбобокса
all_options = [f"{line} — {product}" for line, products in consts.PRODUCTS.items() for product in products]
# Моковые сохраненные отчеты
mock_saved_reports = [
    "Тушь Cabaret Premiere (от 01.06.2024)",
    "Карандаш для глаз Cinecitta (от 28.05.2024)",
    "Помада Matte Lasting (от 15.05.2024)"
]

# ==========================================
# СТРАНИЦА 1: СТАРТОВАЯ (LANDING)
# ==========================================
if st.session_state.page == "landing":
    st.markdown('<div class="hide-sidebar"></div>', unsafe_allow_html=True)

    # Центрирование контента с помощью колонок [1, 2, 1]
    c1, c2, c3 = st.columns([1, 2, 1])

    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("💄 Vivienne Sabo Analytics")
        st.markdown("<p style='color: #6c757d; text-align: center;'>Система интеллектуального анализа отзывов</p>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        product = st.selectbox(
            "Выберите товар для анализа",
            options=all_options,
            index=None,
            placeholder="Начните вводить название товара..."
        )

        if st.button("🚀 Анализ", type="primary", use_container_width=True):
            if product:
                st.session_state.selected_product = product
                st.session_state.report_data = generate_mock_data(product)
                st.session_state.page = "dashboard"
                st.session_state.dashboard_tab = "📊 Дашборд"
                st.rerun()
            else:
                st.warning("Пожалуйста, выберите товар из списка.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Кнопка-ссылка на предыдущие отчеты
        if st.button("📂 Предыдущие отчеты", type="secondary", use_container_width=True):
            st.session_state.page = "reports_list"
            st.rerun()


# ==========================================
# СТРАНИЦА 2: СПИСОК ПРЕДЫДУЩИХ ОТЧЕТОВ
# ==========================================
elif st.session_state.page == "reports_list":
    st.markdown('<div class="hide-sidebar"></div>', unsafe_allow_html=True)

    st.header("📂 Архив отчетов")
    if st.button("← Назад к поиску", type="secondary"):
        st.session_state.page = "landing"
        st.rerun()
    st.divider()

    for report_name in mock_saved_reports:
        # При клике загружаем данные этого отчета и переходим на дашборд
        if st.button(report_name, key=f"rep_{report_name}", use_container_width=True):
            clean_name = report_name.split(" (")[0]  # Убираем дату для чистого имени
            st.session_state.selected_product = clean_name
            st.session_state.report_data = generate_mock_data(clean_name)
            st.session_state.page = "dashboard"
            st.session_state.dashboard_tab = "📊 Дашборд"
            st.rerun()


# ==========================================
# СТРАНИЦА 3: ДАШБОРД (С БОКОВЫМ МЕНЮ)
# ==========================================
elif st.session_state.page == "dashboard":
    st.markdown('<div class="show-sidebar"></div>', unsafe_allow_html=True)

    # --- БОКОВОЕ МЕНЮ ---
    with st.sidebar:
        st.title("💄 VS Analytics")
        st.markdown(f"**Текущий отчет:**\n*{st.session_state.selected_product}*")
        st.divider()

        # Навигация внутри дашборда
        if st.button("📊 Дашборд", use_container_width=True,
                     type="primary" if st.session_state.dashboard_tab == "📊 Дашборд" else "secondary"):
            st.session_state.dashboard_tab = "📊 Дашборд"
            st.rerun()
        if st.button("📝 Отзывы", use_container_width=True,
                     type="primary" if st.session_state.dashboard_tab == "📝 Отзывы" else "secondary"):
            st.session_state.dashboard_tab = "📝 Отзывы"
            st.rerun()
        if st.button("🔗 Источники", use_container_width=True,
                     type="primary" if st.session_state.dashboard_tab == "🔗 Источники" else "secondary"):
            st.session_state.dashboard_tab = "🔗 Источники"
            st.rerun()

        st.divider()
        if st.button("🏠 На главную", type="secondary", use_container_width=True):
            st.session_state.page = "landing"
            st.session_state.selected_product = ""
            st.rerun()

    # --- ОСНОВНОЙ КОНТЕНТ ДАШБОРДА ---
    if not st.session_state.report_data:
        st.warning("Нет данных для отображения.")
    else:
        metrics, segments_df, trends_df, sources_list, reviews_list, ai_text = st.session_state.report_data

        # --- ВКЛАДКА: ДАШБОРД ---
        if st.session_state.dashboard_tab == "📊 Дашборд":
            st.header(f"📊 Дашборд: {st.session_state.selected_product}")
            st.divider()

            # KPI
            st.markdown('<div class="section-header">Ключевые показатели (KPI)</div>', unsafe_allow_html=True)
            kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
            with kpi1:
                st.metric("📝 Всего отзывов", f"{metrics['total_reviews']}", delta="+12%")
            with kpi2:
                st.metric("⚖️ Sentiment Score", f"{metrics['sentiment_score']}%")
            with kpi3:
                st.metric("😊 Позитивные", f"{metrics['pos_pct']}%")
            with kpi4:
                st.metric("😡 Негативные", f"{metrics['neg_pct']}%", delta_color="inverse")
            with kpi5:
                st.metric("⭐ Средний рейтинг", f"{metrics['avg_rating']}/5.0")
            with kpi6:
                st.metric("🔥 Demand Index", f"{metrics['demand_index']}/100")

            st.markdown("<br>", unsafe_allow_html=True)

            # Графики
            st.markdown('<div class="section-header">Аналитика по сегментам</div>', unsafe_allow_html=True)
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                fig_donut = go.Figure(data=[go.Pie(labels=['Позитивные', 'Нейтральные', 'Негативные'],
                                                   values=[metrics['pos_pct'],
                                                           100 - metrics['pos_pct'] - metrics['neg_pct'],
                                                           metrics['neg_pct']], hole=0.4,
                                                   marker_colors=['#28a745', '#6c757d', '#dc3545'])])
                fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
                st.plotly_chart(fig_donut, use_container_width=True)
            with chart_col2:
                fig_bar = px.bar(segments_df, x="Линейка", y="Sentiment Score", color="Цвет",
                                 color_discrete_map="identity", text="Sentiment Score")
                fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=False,
                                      yaxis=dict(range=[-20, 100]))
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">Динамика и Индекс спроса</div>', unsafe_allow_html=True)
            trend_col, demand_col = st.columns([2, 1])
            with trend_col:
                fig_line = px.line(trends_df, x="Месяц", y=["Позитивные", "Негативные"], markers=True,
                                   color_discrete_map={"Позитивные": "#28a745", "Негативные": "#dc3545"})
                fig_line.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
                st.plotly_chart(fig_line, use_container_width=True)
            with demand_col:
                fig_gauge = go.Figure(
                    go.Indicator(mode="gauge+number", value=metrics['demand_index'], domain={'x': [0, 1], 'y': [0, 1]},
                                 title={'text': "Demand Index"},
                                 gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#d63384"},
                                        'steps': [{'range': [0, 40], 'color': "#f8d7da"},
                                                  {'range': [40, 70], 'color': "#fff3cd"},
                                                  {'range': [70, 100], 'color': "#d4edda"}]}))
                fig_gauge.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)

            st.divider()
            st.markdown('<div class="section-header">🤖 ИИ-Вывод и рекомендации</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ai-block">{ai_text}</div>', unsafe_allow_html=True)


        # --- ВКЛАДКА: ОТЗЫВЫ ---
        elif st.session_state.dashboard_tab == "📝 Отзывы":
            st.header(f"📝 Просмотр отзывов: {st.session_state.selected_product}")
            st.divider()
            st.markdown(f"**Всего отображено отзывов: {len(reviews_list)}**")
            st.markdown("<br>", unsafe_allow_html=True)

            for rev in reviews_list:
                stars = "⭐" * rev["rating"] + "☆" * (5 - rev["rating"])
                st.markdown(f"""
                <div class="review-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div><strong>👤 {rev['author']}</strong> <span style="color: #6c757d; font-size: 0.85rem; margin-left: 10px;">{rev['date']}</span></div>
                        <span>{stars}</span>
                    </div>
                    <div style="color: #495057; font-size: 0.95rem; line-height: 1.5;">"{rev['text']}"</div>
                </div>
                """, unsafe_allow_html=True)


        # --- ВКЛАДКА: ИСТОЧНИКИ ---
        elif st.session_state.dashboard_tab == "🔗 Источники":
            st.header(f"🔗 Источники данных: {st.session_state.selected_product}")
            st.divider()
            st.markdown("Отзывы были агрегированы со следующих платформ.")
            st.markdown("<br>", unsafe_allow_html=True)

            for src in sources_list:
                st.markdown(f"""
                <div class="source-card">
                    <div>
                        <strong style="font-size: 1.1rem;">🌐 {src['name']}</strong>
                        <div style="color: #6c757d; font-size: 0.9rem; margin-top: 4px;">Собрано отзывов: <strong>{src['count']}</strong></div>
                    </div>
                    <a href="{src['url']}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #d63384; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;">Перейти ↗</button>
                    </a>
                </div>
                """, unsafe_allow_html=True)