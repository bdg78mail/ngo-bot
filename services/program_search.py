"""
Поиск программ поддержки для семей с детьми с ОВЗ.
"""

import logging
from services.perplexity import search_benefits

log = logging.getLogger("ngo_bot.program_search")


async def search_programs(query: str, region: str = "") -> str:
    """
    Поиск программ поддержки.

    Args:
        query: описание потребности
        region: регион (опционально)

    Returns:
        Текст с найденными программами
    """
    enriched = (
        f"Найди актуальные программы поддержки для семей с детьми с ОВЗ.\n"
        f"Запрос: {query}\n"
    )
    if region:
        enriched += f"Регион: {region}\n"

    enriched += (
        "\nВключи:\n"
        "- Государственные программы\n"
        "- Региональные программы\n"
        "- Программы НКО и фондов\n"
        "- Грантовые программы\n"
        "- Образовательные программы\n"
        "Для каждой программы укажи: название, кто может участвовать, как подать заявку."
    )

    result = await search_benefits(enriched, region=region)
    return result
