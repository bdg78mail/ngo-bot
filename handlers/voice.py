"""
Обработка голосовых сообщений: скачивание → Whisper → текстовый pipeline.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.whisper import download_and_transcribe
from services.perplexity import search_benefits

log = logging.getLogger("ngo_bot.voice")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосового сообщения."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    log.info(f"Голосовое от {user.first_name} (chat_id={chat_id})")

    # Показываем «печатает...»
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Определяем file_id (голосовое или аудиофайл)
    voice = update.message.voice or update.message.audio
    if not voice:
        await update.message.reply_text("Не удалось распознать аудио. Попробуйте ещё раз.")
        return

    # Транскрибируем
    text = await download_and_transcribe(context.bot, voice.file_id)

    if not text:
        await update.message.reply_text(
            "Не удалось распознать речь. Попробуйте:\n"
            "— Говорить чётче\n"
            "— Уменьшить фоновый шум\n"
            "— Написать вопрос текстом"
        )
        return

    # Показываем транскрипцию
    await update.message.reply_text(f"Распознано: <i>{text}</i>", parse_mode="HTML")

    # Отправляем в тот же pipeline что и текст
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    answer = await search_benefits(text)
    await update.message.reply_text(answer)
