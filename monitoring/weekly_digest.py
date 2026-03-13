"""
Еженедельная сводка новостей для пользователей.
Собирает результаты за неделю и формирует дайджест.
"""

import logging
from datetime import datetime
import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

log = logging.getLogger("ngo_bot.weekly_digest")

DIGEST_PROMPT = """Ты создаёшь еженедельный дайджест для родителей детей с ОВЗ.

Формат дайджеста:
1. Заголовок с датами недели
2. Топ-3 самых важных новости
3. Краткий обзор остальных
4. Полезный совет недели

Формат: HTML для Telegram (только <b>, <i>, <a>).
Максимум 2000 символов."""


async def create_weekly_digest(weekly_news: list[dict]) -> str:
    """
    Создать еженедельный дайджест.

    Args:
        weekly_news: все новости за неделю

    Returns:
        Готовый текст дайджеста
    """
    if not weekly_news:
        return (
            f"<b>Дайджест НКО «Потенциал»</b>\n"
            f"<i>{datetime.now().strftime('%d.%m.%Y')}</i>\n\n"
            "На этой неделе значимых новостей не было.\n"
            "Следите за обновлениями!"
        )

    # Собираем все новости в один текст
    all_news = "\n\n".join(
        item.get("content", "")[:300]
        for item in weekly_news[:10]  # Максимум 10 новостей
    )

    if not ANTHROPIC_API_KEY:
        return f"<b>Дайджест недели</b>\n\n{all_news[:2000]}"

    try:
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            system=DIGEST_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Создай дайджест из этих новостей:\n\n{all_news}",
            }],
        )
        return message.content[0].text
    except Exception as e:
        log.error(f"Ошибка создания дайджеста: {e}")
        return f"<b>Дайджест недели</b>\n\n{all_news[:2000]}"
