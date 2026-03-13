"""
Сложные консультации через Claude API (Anthropic SDK).
"""

import logging
import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

log = logging.getLogger("ngo_bot.claude")

SYSTEM_PROMPT = """Ты — опытный консультант НКО «Потенциал», помогающий семьям с детьми с ОВЗ.

Ты проводишь персональные консультации. В отличие от быстрого поиска, здесь ты:
1. Анализируешь конкретную ситуацию семьи
2. Даёшь пошаговые рекомендации
3. Указываешь, какие документы нужны
4. Рекомендуешь, куда обратиться
5. Учитываешь региональную специфику

Формат ответа:
- Структурируй ответ с заголовками
- Указывай конкретные шаги
- Добавляй ссылки на законы, если применимо
- Будь тёплым и поддерживающим
- Предупреждай, если нужна помощь юриста"""


async def consult(query: str, context: str = "") -> str:
    """
    Персональная консультация через Claude.

    Args:
        query: вопрос/ситуация пользователя
        context: дополнительный контекст (регион, возраст, категория)

    Returns:
        Текст консультации
    """
    if not ANTHROPIC_API_KEY:
        log.error("ANTHROPIC_API_KEY не задан")
        return "Извините, сервис консультаций временно недоступен."

    full_query = query
    if context:
        full_query = f"{query}\n\nДополнительная информация: {context}"

    try:
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        message = await client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": full_query}],
        )
        return message.content[0].text
    except Exception as e:
        log.error(f"Claude API ошибка: {e}")
        return "Извините, не удалось провести консультацию. Попробуйте позже."
