"""
НКО Потенциал — AI-помощник для родителей детей с ОВЗ.
Telegram: @special_kids_benefits_bot

Точка входа: python bot.py
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, BOT_MODE
from handlers.commands import cmd_start, cmd_help, cmd_about, cmd_share, cmd_feedback
from handlers.text import handle_text
from handlers.voice import handle_voice
from handlers.callbacks import handle_callback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger("ngo_bot")


def main():
    """Запуск бота."""
    if not BOT_TOKEN:
        log.error("NGO_BOT_TOKEN не задан. Проверьте .env")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("share", cmd_share))
    app.add_handler(CommandHandler("feedback", cmd_feedback))

    # Callback-кнопки
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Голосовые сообщения
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))

    # Текстовые сообщения (последний — catch-all)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    log.info("НКО Потенциал: бот запущен (@special_kids_benefits_bot)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
