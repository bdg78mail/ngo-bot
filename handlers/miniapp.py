"""
Обработка данных из Telegram Mini App.
Mini App отправляет POST с данными: region, age, category, question.
"""

import logging
import re
from services.router import classify_question
from services.perplexity import search_benefits
from services.recommendations import generate_recommendations

log = logging.getLogger("ngo_bot.miniapp")


async def process_miniapp_request(data: dict) -> dict:
    """
    Обработка запроса от Mini App.

    Args:
        data: {
            "type": "consultation" | "quick_answer",
            "region": str,
            "regionName": str,
            "age": str,
            "ageName": str,
            "category": str,
            "categoryName": str,
            "question": str (для consultation),
            "question_id": str (для quick_answer),
            "user_id": str,
        }

    Returns:
        {"status": "ok", "answer": str} или {"status": "error", "message": str}
    """
    request_type = data.get("type", "unknown")
    region = data.get("regionName", data.get("region", ""))
    age = data.get("ageName", data.get("age", ""))
    category = data.get("categoryName", data.get("category", ""))
    question = data.get("question", data.get("question_text", ""))
    user_id = data.get("user_id", "webapp_user")

    log.info(f"Mini App запрос от {user_id}: тип={request_type}, регион={region}")

    try:
        if request_type == "consultation":
            # Полная консультация через Perplexity
            answer = await search_benefits(
                query=question or f"Льготы для ребёнка с ОВЗ",
                region=region,
                age=age,
                category=category,
            )
            return {"status": "ok", "answer": _clean_md_for_web(answer)}

        elif request_type == "quick_answer":
            # Быстрый ответ — генерация рекомендаций по параметрам
            answer = await generate_recommendations(
                region=region,
                age=age,
                category=category,
                question=question,
            )
            return {"status": "ok", "answer": _clean_md_for_web(answer)}

        else:
            return {"status": "error", "message": f"Неизвестный тип запроса: {request_type}"}

    except Exception as e:
        log.error(f"Ошибка обработки Mini App: {e}")
        return {"status": "error", "message": "Произошла ошибка. Попробуйте позже."}


def _clean_md_for_web(text: str) -> str:
    """Очистка Markdown для отображения в Mini App (plain text)."""
    # Убираем сноски [1][2]
    text = re.sub(r"(\[\d+\])+", "", text)
    # Заголовки: #### Текст → Текст
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Жирный: **текст** → текст
    text = re.sub(r"\*{2}(.+?)\*{2}", r"\1", text)
    # Курсив: *текст* → текст
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    # Убираем --- разделители
    text = re.sub(r"^-{3,}$", "", text, flags=re.MULTILINE)
    # Маркированные списки: - → •
    text = re.sub(r"^[-*]\s+", "• ", text, flags=re.MULTILINE)
    # Лишние пустые строки
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
