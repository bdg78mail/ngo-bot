"""
Обработка текстовых сообщений — полный pipeline.
Роутинг: быстрый ответ → Perplexity → Claude (по режиму).
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.router import classify_question
from services.perplexity import search_benefits
from services.claude import consult
from services.recommendations import generate_recommendations
from services.program_search import search_programs
from services.pdf_report import generate_and_send_pdf
from services.formatter import md_to_telegram_html
from handlers.feedback import save_user_feedback

log = logging.getLogger("ngo_bot.text")

# Максимальная длина сообщения Telegram
MAX_MESSAGE_LENGTH = 4096


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик текстовых сообщений."""
    text = update.message.text
    chat_id = update.effective_chat.id
    user = update.effective_user

    log.info(f"Текст от {user.first_name} (chat_id={chat_id}): {text[:80]}")

    # Проверяем, ожидается ли фидбек
    if context.user_data.get("awaiting_feedback"):
        context.user_data["awaiting_feedback"] = False
        await save_user_feedback(update, text)
        return

    # Определяем режим (из callback-кнопки или автоматически)
    mode = context.user_data.pop("mode", "")

    # Классифицируем вопрос
    result = classify_question(text, mode)
    question_type = result["type"]

    log.info(f"Тип вопроса: {question_type}")

    # Показываем «печатает...»
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    if question_type == "quick_answer":
        # Быстрый ответ по ключевым словам
        answer = result.get("quick_answer", "")
        if answer:
            await _send_long_message(update, answer, context)
        else:
            # Фолбек на Perplexity если ответ пустой
            answer = await search_benefits(text)
            await _send_long_message(update, answer, context)

    elif question_type == "consultation":
        # Консультация: сначала Perplexity для фактов, потом Claude для анализа
        answer = await search_benefits(text)
        await _send_long_message(update, answer, context)

    elif question_type == "pdf_report":
        # Генерация PDF-отчёта
        await update.message.reply_text("Формирую PDF-отчёт, это может занять минуту...")
        await generate_and_send_pdf(update, context, text)

    elif question_type == "program_search":
        # Поиск программ поддержки
        await update.message.reply_text("Ищу подходящие программы...")
        answer = await search_programs(text)
        await _send_long_message(update, answer, context)

    else:
        # Неизвестный тип — отправляем в Perplexity
        answer = await search_benefits(text)
        await _send_long_message(update, answer, context)


async def _send_long_message(update: Update, text: str, context: ContextTypes.DEFAULT_TYPE = None, format_md: bool = True):
    """Отправка длинного сообщения с форматированием и кнопкой «Прослушать»."""
    # Сохраняем оригинал для TTS (до форматирования)
    raw_text = text

    if format_md:
        text = md_to_telegram_html(text)

    # Кнопка «Прослушать»
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Прослушать", callback_data="tts_listen")]
    ])

    if len(text) <= MAX_MESSAGE_LENGTH:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        # Разбиваем по абзацам
        parts = []
        current = ""
        for line in text.split("\n"):
            if len(current) + len(line) + 1 > MAX_MESSAGE_LENGTH:
                parts.append(current)
                current = line
            else:
                current = current + "\n" + line if current else line
        if current:
            parts.append(current)

        # Все части кроме последней — без кнопки
        for part in parts[:-1]:
            await update.message.reply_text(part, parse_mode="HTML")
        # Последняя часть — с кнопкой
        await update.message.reply_text(parts[-1], parse_mode="HTML", reply_markup=keyboard)

    # Сохраняем текст для TTS
    if context is not None:
        context.chat_data["last_answer"] = raw_text
