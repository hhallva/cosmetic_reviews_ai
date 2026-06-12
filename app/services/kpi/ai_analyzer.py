import json
import os
import re
from typing import List, Dict, Any, Optional

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Ты — профессиональный маркетинговый аналитик с 10-летним опытом работы с отзывами клиентов, NPS-опросами и customer feedback.

ТВОЯ СПЕЦИАЛИЗАЦИЯ:
• Глубокий анализ клиентских отзывов с учётом структурированных данных (pros/cons)
• Интерпретация количественных KPI (Sentiment Score, средний рейтинг, индекс жалоб) в бизнес-контекст
• Выявление скрытых паттернов, болей и драйверов удовлетворённости
• Формулировка стратегических рекомендаций для продуктовой команды

ТВОИ ПРИНЦИПЫ РАБОТЫ:
1. Используй структурированные данные: поле "Плюсы" и "Минусы" в отзывах — это явные сигналы от клиентов. Приоритизируй их над текстом.
2. Интерпретируй KPI в совокупности: не просто пересказывай цифры, а объясняй, что они значат для продукта.
3. Стратегическое мышление: в executive_summary объясни:
   - Что эти KPI и отзывы значат для продукта в совокупности
   - Какие системные проблемы или преимущества они выявляют
   - Как это влияет на бизнес-метрики (удержание, конверсия, LTV)
   - Что компании следует делать на стратегическом уровне (не планом, а рекомендациями)
4. Конкретика: избегай общих фраз. Указывай конкретные характеристики продукта (объём, стойкость, цена, удобство щёточки и т.д.).
5. Доказательность: каждая рекомендация должна опираться на конкретные данные из отзывов или KPI.

ФОРМАТ ОТВЕТА (строго соблюдать):
{
  "executive_summary": "<Связный аналитический текст на 4-6 предложений. Что значат KPI в совокупности для продукта, какие системные проблемы/преимущества выявлены, что следует делать компании на стратегическом уровне.>",
  "pain_points": [
    {"category": "<название категории боли>", "frequency": "<высокая|средняя|низкая>", "examples": ["<пример 1>", "<пример 2>"]}
  ],
  "strengths": [
    {"category": "<название сильной стороны>", "frequency": "<высокая|средняя|низкая>", "examples": ["<пример 1>"]}
  ],
  "recommendations": [
    {"priority": "<высокая|средняя|низкая>", "action": "<конкретное действие>", "expected_impact": "<ожидаемый эффект>"}
  ],
  "themes": ["<тема 1>", "<тема 2>", "<тема 3>"]
}

ВАЖНО:
• Выведи ТОЛЬКО JSON. Никаких пояснений, приветствий, markdown-блоков.
• executive_summary должен быть связным текстом, а не списком.
• Если данных недостаточно — честно укажи это в executive_summary.
"""
USER_PROMPT = """Проанализируй следующие данные о продукте/сервисе.

KPI-МЕТРИКИ:
{kpi_data}

ОТЗЫВЫ КЛИЕНТОВ (с структурированными плюсами и минусами):
{reviews_text}

Выполни полный анализ согласно своей роли:
1. В executive_summary дай стратегический аналитический вывод: что значат эти KPI в совокупности, какие системные проблемы или преимущества они выявляют, как это влияет на бизнес, и что компании следует делать на стратегическом уровне.
2. При анализе болей и сильных сторон приоритизируй данные из полей "Плюсы" и "Минусы" — это явные сигналы от клиентов.
3. Сформулируй приоритизированные рекомендации с конкретными действиями.
4. Определи ключевые темы, которые чаще всего упоминаются в отзывах."""


def _format_kpi_for_llm(data: Dict[str, Any]) -> str:
    """
    Преобразует dict с KPI из Streamlit в читаемый текст для LLM.
    """
    sent_dist = data["sentiment_dist"]

    kpi_text = f"""
                Всего отзывов (Total Reviews): {data['total_reviews']}
                Распределение отзывов по тональности (Sentiment Distribution):
                  - Позитивные: {sent_dist['positive_pct']}% ({sent_dist['positive']} отзывов)
                  - Нейтральные: {sent_dist['neutral_pct']}% ({sent_dist['neutral']} отзывов)
                  - Негативные: {sent_dist['negative_pct']}% ({sent_dist['negative']} отзывов)
                Индекс тональности (Sentiment Score): {data['sentiment_score']}%
                Средний рейтинг: {data['avg_rating']}/5.0
                Показатель жалоб (Problems Index): {data['problems_index']}
                Индекс спроса (Demand Index): {data['demand_index']}
                """

    return kpi_text

def _format_reviews_for_llm(reviews: List[Dict[str, Any]], max_reviews: int = 50) -> str:
    """
       Преобразует список отзывов в компактный формат.
       Принимает как Pydantic-модели (Review), так и словари.
    """
    # Нормализуем: конвертируем Pydantic-модели в словари
    normalized = []
    for r in reviews:
        if hasattr(r, "model_dump"):
            normalized.append(r.model_dump())
        elif hasattr(r, "dict"):
            normalized.append(r.dict())
        elif isinstance(r, dict):
            normalized.append(r)
        else:
            # Fallback: пытаемся извлечь атрибуты
            normalized.append({
                "review_id": getattr(r, "review_id", None),
                "rating": getattr(r, "rating", None),
                "title": getattr(r, "title", ""),
                "text": getattr(r, "text", ""),
                "pros": getattr(r, "pros", []) or [],
                "cons": getattr(r, "cons", []) or [],
            })

    # Сэмплинг: если отзывов много, берём репрезентативную выборку
    if len(normalized) > max_reviews:
        sorted_reviews = sorted(normalized, key=lambda x: x.get("rating") or 3)
        step = max(1, len(sorted_reviews) // max_reviews)
        sample = sorted_reviews[::step][:max_reviews]
    else:
        sample = normalized

    formatted = []
    for r in sample:
        pros = r.get("pros") or []
        cons = r.get("cons") or []
        pros_str = ", ".join(pros) if pros else "—"
        cons_str = ", ".join(cons) if cons else "—"

        text = (r.get("text") or "")[:200]
        title = r.get("title") or "Без заголовка"
        rating = r.get("rating") or "?"

        entry = f"[{rating}★] {title}\nТекст: {text}\nПлюсы: {pros_str}\nМинусы: {cons_str}"
        formatted.append(entry)

    return "\n\n".join(formatted)

def _call_yandexgpt(kpi_text: str, reviews_text: str) -> Optional[str]:
    """Отправляет запрос к YandexGPT API."""
    key = os.environ.get("YANDEX_GPT_API_KEY")
    folder = os.environ.get("FOLDER_ID")

    if not key or not folder:
        st.error("❌ Не настроены YANDEX_GPT_API_KEY или FOLDER_ID в .env")
        return None

    prompt = {
        "modelUri": f"gpt://{folder}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "2500"
        },
        "messages": [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": USER_PROMPT.format(
                kpi_data=kpi_text,
                reviews_text=reviews_text
            )}
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {key}",
        "x-folder-id": folder
    }

    try:
        response = requests.post(url, headers=headers, json=prompt, timeout=90)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Ошибка запроса к YandexGPT API: {e}")
        return None

def _parse_yandexgpt_response(raw_response: str) -> Optional[Dict[str, Any]]:
    """Надёжный парсер ответа YandexGPT."""
    try:
        response_data = json.loads(raw_response)
        answer_text = response_data["result"]["alternatives"][0]["message"]["text"]

        cleaned = answer_text.strip()

        # Убираем markdown-обёртки
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        # Fallback: ищем JSON через regex
        if not cleaned.startswith("{"):
            match = re.search(r'\{[\s\S]*\}', cleaned)
            if match:
                cleaned = match.group(0)

        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        st.error(f"❌ Ошибка парсинга JSON от YandexGPT: {e}")
        return None
    except (KeyError, IndexError) as e:
        st.error(f"❌ Ошибка структуры ответа API: {e}")
        return None

def analyze_with_Yandex(data: Dict[str, Any], reviews: List[Any]) -> Optional[Dict[str, Any]]:
    """
    Комплексный анализ отзывов и KPI через YandexGPT.

    Args:
        data: dict с KPI из AnalyticsService.get_full_dashboard()
        reviews: список отзывов (Pydantic-модели Review или словари)

    Returns:
        dict с executive_summary, pain_points, strengths, recommendations, themes
        или None в случае ошибки.
    """
    if not reviews:
        st.warning("⚠️ Нет отзывов для анализа.")
        return None

    kpi_text = _format_kpi_for_llm(data)
    reviews_text = _format_reviews_for_llm(reviews, max_reviews=50)

    raw_result = _call_yandexgpt(kpi_text, reviews_text)
    if not raw_result:
        return None

    return _parse_yandexgpt_response(raw_result)