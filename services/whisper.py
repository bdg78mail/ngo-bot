"""
Транскрипция голосовых сообщений через OpenAI Whisper.
"""

import logging
import tempfile
import os
from openai import AsyncOpenAI

from config import OPENAI_API_KEY

log = logging.getLogger("ngo_bot.whisper")


async def transcribe(file_path: str) -> str:
    """
    Транскрибировать аудиофайл через Whisper.

    Args:
        file_path: путь к аудиофайлу (ogg/mp3/wav)

    Returns:
        Текст транскрипции
    """
    if not OPENAI_API_KEY:
        log.error("OPENAI_API_KEY не задан")
        return ""

    try:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        with open(file_path, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru",
            )
        text = transcript.text.strip()
        log.info(f"Транскрипция ({len(text)} символов): {text[:80]}")
        return text
    except Exception as e:
        log.error(f"Whisper ошибка: {e}")
        return ""


async def download_and_transcribe(bot, file_id: str) -> str:
    """
    Скачать файл из Telegram и транскрибировать.

    Args:
        bot: объект бота Telegram
        file_id: ID файла в Telegram

    Returns:
        Текст транскрипции
    """
    try:
        # Скачиваем файл
        file = await bot.get_file(file_id)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name
            await file.download_to_drive(tmp_path)

        # Транскрибируем
        text = await transcribe(tmp_path)

        # Удаляем временный файл
        os.unlink(tmp_path)

        return text
    except Exception as e:
        log.error(f"Ошибка скачивания/транскрипции: {e}")
        return ""
