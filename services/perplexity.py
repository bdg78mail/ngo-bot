"""
Поиск льгот через Perplexity (OpenRouter или Perplexity API напрямую).
"""

import logging
import httpx

from config import OPENROUTER_API_KEY, PERPLEXITY_API_KEY, PERPLEXITY_MODEL

log = logging.getLogger("ngo_bot.perplexity")

# Системный промпт для поиска льгот
SYSTEM_PROMPT = """Ты — AI-помощник НКО «Потенциал» для родителей детей с ОВЗ (ограниченными возможностями здоровья) в России.

Твоя задача — находить актуальную информацию о:
- Льготах и выплатах для семей с детьми-инвалидами
- Социальных услугах и программах поддержки
- Оформлении инвалидности и ИППСУ
- Образовательных льготах
- Медицинской помощи и реабилитации
- Региональных программах

Правила:
1. Отвечай на русском языке
2. Указывай конкретные суммы, сроки, документы
3. Ссылайся на действующие законы и нормативные акты
4. Различай федеральные и региональные льготы
5. Если информация может быть устаревшей, предупреди об этом
6. Будь доброжелателен и поддерживающ — ты общаешься с родителями
7. Не давай юридических заключений — рекомендуй обратиться к специалисту для важных решений"""


async def search_benefits(query: str, region: str = "", age: str = "", category: str = "") -> str:
    """
    Поиск информации о льготах через Perplexity.

    Args:
        query: вопрос пользователя
        region: регион (опционально)
        age: возраст ребёнка (опционально)
        category: категория инвалидности (опционально)

    Returns:
        Текст ответа от Perplexity
    """
    # Обогащаем запрос контекстом
    enriched_query = query
    context_parts = []
    if region:
        context_parts.append(f"Регион: {region}")
    if age:
        context_parts.append(f"Возраст ребёнка: {age}")
    if category:
        context_parts.append(f"Категория: {category}")
    if context_parts:
        enriched_query = f"{query}\n\nКонтекст: {', '.join(context_parts)}"

    # Пробуем Perplexity напрямую, если есть ключ
    if PERPLEXITY_API_KEY:
        return await _call_perplexity_direct(enriched_query)

    # Иначе через OpenRouter
    if OPENROUTER_API_KEY:
        return await _call_openrouter(enriched_query)

    log.error("Нет ключей API: ни PERPLEXITY_API_KEY, ни OPENROUTER_API_KEY")
    return "Извините, сервис временно недоступен. Попробуйте позже."


async def _call_perplexity_direct(query: str) -> str:
    """Вызов Perplexity API напрямую."""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        "temperature": 0.3,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        log.error(f"Perplexity API ошибка: {e}")
        # Фолбек на OpenRouter
        if OPENROUTER_API_KEY:
            log.info("Фолбек на OpenRouter")
            return await _call_openrouter(query)
        return "Извините, не удалось получить ответ. Попробуйте позже."


async def _call_openrouter(query: str) -> str:
    """Вызов Perplexity через OpenRouter."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        "temperature": 0.3,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        log.error(f"OpenRouter ошибка: {e}")
        return "Извините, не удалось получить ответ. Попробуйте позже."
