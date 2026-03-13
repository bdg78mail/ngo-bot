"""
Анализ релевантности найденных новостей.
Фильтрует шум, оставляет только важные для родителей новости.
"""

import logging
import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

log = logging.getLogger("ngo_bot.relevance")

ANALYSIS_PROMPT = """Ты анализируешь новости для родителей детей с ОВЗ.

Оцени релевантность каждой новости по шкале 1-10:
- 8-10: очень важно (новые выплаты, изменения закона, новые программы)
- 5-7: полезно (обновления, разъяснения, региональные новости)
- 1-4: не релевантно (общие новости, реклама)

Для каждой новости верни:
1. Оценка релевантности (число)
2. Краткое описание (1-2 предложения)
3. Категория: выплаты / законодательство / программы / образование / медицина / другое

Формат: JSON массив."""


async def analyze_relevance(news_items: list[dict]) -> list[dict]:
    """
    Анализ релевантности новостей через Claude.

    Args:
        news_items: список новостей от news_scanner

    Returns:
        Отфильтрованные и оценённые новости (score >= 5)
    """
    if not news_items:
        return []

    if not ANTHROPIC_API_KEY:
        log.warning("ANTHROPIC_API_KEY не задан, пропускаем анализ релевантности")
        return news_items

    # Формируем текст для анализа
    news_text = "\n\n---\n\n".join(
        f"Запрос: {item['query']}\nСодержание: {item['content'][:500]}"
        for item in news_items
    )

    try:
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            system=ANALYSIS_PROMPT,
            messages=[{"role": "user", "content": news_text}],
        )
        response = message.content[0].text

        # Пытаемся распарсить JSON
        import json
        try:
            analyzed = json.loads(response)
        except json.JSONDecodeError:
            log.warning("Не удалось распарсить ответ Claude как JSON")
            return news_items

        # Фильтруем по релевантности >= 5
        relevant = [
            {**item, **analysis}
            for item, analysis in zip(news_items, analyzed)
            if isinstance(analysis, dict) and analysis.get("score", analysis.get("relevance", 0)) >= 5
        ]

        log.info(f"После анализа: {len(relevant)} из {len(news_items)} релевантны")
        return relevant

    except Exception as e:
        log.error(f"Ошибка анализа релевантности: {e}")
        return news_items
