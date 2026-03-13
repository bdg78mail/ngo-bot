"""
Формирование сообщений из релевантных новостей для отправки пользователям.
"""

import logging
import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

log = logging.getLogger("ngo_bot.message_creator")

FORMAT_PROMPT = """Ты формируешь сообщения для Telegram-канала НКО «Потенциал».
Аудитория: родители детей с ОВЗ.

Правила:
1. Пиши просто и понятно
2. Используй эмодзи уместно
3. Структурируй с заголовками
4. Указывай источники
5. Длина: не более 1000 символов на одну новость
6. Формат: HTML для Telegram (только <b>, <i>, <a>)"""


async def create_messages(relevant_news: list[dict]) -> list[str]:
    """
    Создать готовые сообщения для Telegram из релевантных новостей.

    Args:
        relevant_news: отфильтрованные новости

    Returns:
        Список готовых сообщений для отправки
    """
    if not relevant_news:
        return []

    if not ANTHROPIC_API_KEY:
        # Фолбек: просто форматируем как есть
        return [_simple_format(item) for item in relevant_news]

    messages = []
    for item in relevant_news:
        try:
            client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            message = await client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=500,
                system=FORMAT_PROMPT,
                messages=[{
                    "role": "user",
                    "content": f"Создай сообщение для Telegram из этой новости:\n{item.get('content', '')[:800]}",
                }],
            )
            messages.append(message.content[0].text)
        except Exception as e:
            log.error(f"Ошибка создания сообщения: {e}")
            messages.append(_simple_format(item))

    return messages


def _simple_format(item: dict) -> str:
    """Простое форматирование новости."""
    content = item.get("content", "")[:800]
    return f"<b>Новость</b>\n\n{content}"
