"""
Генерация персональных рекомендаций по льготам.
Использует Claude для анализа ситуации + Perplexity для фактов.
"""

import logging
from services.perplexity import search_benefits
from services.claude import consult

log = logging.getLogger("ngo_bot.recommendations")


async def generate_recommendations(
    region: str = "",
    age: str = "",
    category: str = "",
    question: str = "",
) -> str:
    """
    Генерация персональных рекомендаций.

    Args:
        region: регион проживания
        age: возраст ребёнка
        category: категория инвалидности
        question: дополнительный вопрос

    Returns:
        Текст рекомендаций
    """
    # Формируем запрос
    parts = ["Составь персональные рекомендации по льготам и поддержке для семьи:"]
    if region:
        parts.append(f"Регион: {region}")
    if age:
        parts.append(f"Возраст ребёнка: {age}")
    if category:
        parts.append(f"Категория: {category}")
    if question:
        parts.append(f"Дополнительный вопрос: {question}")

    query = "\n".join(parts)

    # Сначала ищем актуальные данные через Perplexity
    facts = await search_benefits(query, region=region, age=age, category=category)

    # Затем Claude формирует персональные рекомендации
    context = f"Актуальные данные из поиска:\n{facts}"
    recommendations = await consult(query, context=context)

    return recommendations
