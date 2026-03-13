"""
Маршрутизация вопросов: быстрый ответ vs консультация через AI.
"""

import json
import logging
import os

log = logging.getLogger("ngo_bot.router")

# Загрузка ключевых слов для быстрых ответов
KEYWORDS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "keywords.json")
_keywords_data = {}

def _load_keywords():
    """Загрузка keywords.json."""
    global _keywords_data
    try:
        with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
            _keywords_data = json.load(f)
        log.info(f"Загружено {len(_keywords_data)} категорий ключевых слов")
    except FileNotFoundError:
        log.warning(f"Файл {KEYWORDS_PATH} не найден, быстрые ответы отключены")
    except Exception as e:
        log.error(f"Ошибка загрузки keywords.json: {e}")

_load_keywords()


def classify_question(text: str, mode: str = "") -> dict:
    """
    Классификация вопроса: quick_answer или consultation.

    Args:
        text: текст вопроса
        mode: принудительный режим (если пользователь выбрал кнопку)

    Returns:
        dict с полями:
            type: "quick_answer" | "consultation" | "pdf_report" | "program_search"
            quick_answer: текст быстрого ответа (если type == quick_answer)
            category: найденная категория (если есть)
    """
    # Принудительный режим (пользователь нажал кнопку)
    if mode in ("consultation", "pdf_report", "program_search"):
        return {"type": mode}

    # Проверка ключевых слов для быстрого ответа
    text_lower = text.lower()
    for category, data in _keywords_data.items():
        keywords = data.get("keywords", [])
        for kw in keywords:
            if kw.lower() in text_lower:
                return {
                    "type": "quick_answer",
                    "quick_answer": data.get("answer", ""),
                    "category": category,
                }

    # По умолчанию — консультация через Perplexity
    return {"type": "consultation"}
