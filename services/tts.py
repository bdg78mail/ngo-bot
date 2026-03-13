"""
TTS (Text-to-Speech) — озвучка ответов через OpenAI TTS.
Голос: nova (женский, дружелюбный).
"""

import logging
import re
import tempfile
from openai import AsyncOpenAI

from config import OPENAI_API_KEY

log = logging.getLogger("ngo_bot.tts")

# Лимит символов для TTS (OpenAI принимает до 4096)
MAX_TTS_CHARS = 4000


async def synthesize(text: str) -> str | None:
    """
    Синтез речи из текста через OpenAI TTS.

    Args:
        text: текст для озвучки (Markdown/HTML — будет очищен)

    Returns:
        Путь к .ogg аудиофайлу или None при ошибке
    """
    if not OPENAI_API_KEY:
        log.warning("OPENAI_API_KEY не задан — TTS недоступен")
        return None

    # Очищаем от разметки для естественной речи
    clean = _clean_for_speech(text)

    if not clean.strip():
        log.warning("Пустой текст после очистки — нечего озвучивать")
        return None

    # Обрезаем если слишком длинный (по предложениям)
    if len(clean) > MAX_TTS_CHARS:
        clean = _truncate_smart(clean, MAX_TTS_CHARS)

    try:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=clean,
            response_format="opus",
        )

        # Сохраняем в временный файл
        tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
        tmp.write(response.content)
        tmp.close()

        log.info(f"TTS: сгенерировано {len(clean)} символов → {tmp.name}")
        return tmp.name

    except Exception as e:
        log.error(f"OpenAI TTS ошибка: {e}")
        return None


def _clean_for_speech(text: str) -> str:
    """Очистка текста от разметки для естественной речи."""
    # Убираем HTML-теги
    text = re.sub(r"<[^>]+>", "", text)
    # Убираем HTML-сущности
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # Убираем сноски [1][2]
    text = re.sub(r"(\[\d+\])+", "", text)
    # Убираем Markdown-заголовки
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Убираем жирный/курсив
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    # Маркеры списков → пауза
    text = re.sub(r"^[-•]\s+", "— ", text, flags=re.MULTILINE)
    # Убираем горизонтальные линии
    text = re.sub(r"^-{3,}$", "", text, flags=re.MULTILINE)
    # Убираем ссылки [текст](url) → текст
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Лишние пустые строки
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _truncate_smart(text: str, max_chars: int) -> str:
    """Обрезка текста по предложениям (не на полуслове)."""
    if len(text) <= max_chars:
        return text

    # Ищем последнюю точку/восклицание/вопрос до лимита
    truncated = text[:max_chars]
    last_sentence = max(
        truncated.rfind(". "),
        truncated.rfind("! "),
        truncated.rfind("? "),
        truncated.rfind(".\n"),
        truncated.rfind("!\n"),
        truncated.rfind("?\n"),
    )

    if last_sentence > max_chars // 2:
        return truncated[: last_sentence + 1]

    return truncated
