"""
TTS (Text-to-Speech) — озвучка ответов.
Поддержка: Yandex SpeechKit, Sber Salute Speech.
Не приоритет — заглушка для будущей реализации.
"""

import logging
import httpx
import tempfile

from config import YANDEX_TTS_API_KEY, SBER_TTS_API_KEY

log = logging.getLogger("ngo_bot.tts")


async def synthesize(text: str, engine: str = "yandex") -> str | None:
    """
    Синтез речи из текста.

    Args:
        text: текст для озвучки
        engine: "yandex" или "sber"

    Returns:
        Путь к аудиофайлу или None
    """
    if engine == "yandex" and YANDEX_TTS_API_KEY:
        return await _yandex_tts(text)
    elif engine == "sber" and SBER_TTS_API_KEY:
        return await _sber_tts(text)
    else:
        log.warning(f"TTS движок {engine} не настроен")
        return None


async def _yandex_tts(text: str) -> str | None:
    """Yandex SpeechKit TTS."""
    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    headers = {"Authorization": f"Api-Key {YANDEX_TTS_API_KEY}"}
    data = {
        "text": text[:1000],  # Лимит Yandex
        "lang": "ru-RU",
        "voice": "alena",
        "emotion": "friendly",
        "format": "oggopus",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, data=data)
            resp.raise_for_status()

            tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
            tmp.write(resp.content)
            tmp.close()
            return tmp.name
    except Exception as e:
        log.error(f"Yandex TTS ошибка: {e}")
        return None


async def _sber_tts(text: str) -> str | None:
    """Sber Salute Speech TTS."""
    # TODO: реализовать Sber TTS API
    log.warning("Sber TTS пока не реализован")
    return None
