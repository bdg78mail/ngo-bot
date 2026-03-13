"""
Мониторинг изменений законодательства в сфере поддержки детей с ОВЗ.
"""

import logging
from services.perplexity import search_benefits

log = logging.getLogger("ngo_bot.legislation")

LEGISLATION_QUERIES = [
    "новые законы поддержка детей инвалидов 2026 Россия",
    "изменения федеральный закон 181-ФЗ о социальной защите инвалидов",
    "постановления правительства детская инвалидность 2026",
    "изменения порядок оформления инвалидности дети 2026",
]


async def check_legislation_changes() -> list[dict]:
    """
    Проверка изменений законодательства.

    Returns:
        Список найденных изменений
    """
    log.info("Проверка изменений законодательства")
    changes = []

    for query in LEGISLATION_QUERIES:
        try:
            content = await search_benefits(query)
            if content and "Извините" not in content:
                changes.append({
                    "query": query,
                    "content": content,
                    "type": "legislation",
                })
        except Exception as e:
            log.error(f"Ошибка мониторинга законодательства: {e}")

    log.info(f"Найдено {len(changes)} изменений законодательства")
    return changes
