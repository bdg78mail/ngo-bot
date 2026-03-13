"""
Ежедневный скан новостей о льготах и законах для детей с ОВЗ.
Цепочка: news_scanner (A) → relevance_analyzer (B) → message_creator (C) → weekly_digest (D)
"""

import logging
from datetime import datetime
from services.perplexity import search_benefits

log = logging.getLogger("ngo_bot.news_scanner")

# Запросы для ежедневного сканирования
SCAN_QUERIES = [
    "новости льготы дети инвалиды ОВЗ 2026",
    "изменения законодательства дети инвалидность социальная поддержка",
    "новые программы поддержки семьи дети ОВЗ Россия",
    "выплаты пособия дети инвалиды изменения",
]


async def scan_daily_news() -> list[dict]:
    """
    Ежедневный скан новостей.

    Returns:
        Список новостей: [{"query": ..., "content": ..., "date": ...}]
    """
    log.info("Запуск ежедневного скана новостей")
    results = []

    for query in SCAN_QUERIES:
        try:
            content = await search_benefits(query)
            if content and "Извините" not in content:
                results.append({
                    "query": query,
                    "content": content,
                    "date": datetime.now().isoformat(),
                })
                log.info(f"Найдены новости по запросу: {query[:50]}")
        except Exception as e:
            log.error(f"Ошибка скана по запросу '{query[:50]}': {e}")

    log.info(f"Скан завершён: найдено {len(results)} результатов")
    return results
