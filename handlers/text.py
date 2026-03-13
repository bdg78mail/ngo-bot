"""
Обработка текстовых сообщений — полный pipeline.
Роутинг: быстрый ответ → Perplexity → Claude (по режиму).
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.router import classify_question
from services.perplexity import search_benefits
from services.claude import consult
from services.recommendations import generate_recommendations
from services.program_search import search_programs
from services.pdf_report import generate_and_send_pdf
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
            await _send_long_message(update, answer)
        else:
            # Фолбек на Perplexity если ответ пустой
            answer = await search_benefits(text)
            await _send_long_message(update, answer)

    elif question_type == "consultation":
        # Консультация: сначала Perplexity для фактов, потом Claude для анализа
        answer = await search_benefits(text)
        await _send_long_message(update, answer)

    elif question_type == "pdf_report":
        # Генерация PDF-отчёта
        await update.message.reply_text("Формирую PDF-отчёт, это может занять минуту...")
        await generate_and_send_pdf(update, context, text)

    elif question_type == "program_search":
        # Поиск программ поддержки
        await update.message.reply_text("Ищу подходящие программы...")
        answer = await search_programs(text)
        await _send_long_message(update, answer)

    else:
        # Неизвестный тип — отправляем в Perplexity
        answer = await search_benefits(text)
        await _send_long_message(update, answer)


async def _send_long_message(update: Update, text: str):
    """Отправка длинного сообщения с разбивкой по частям."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        await update.message.reply_text(text)
        return

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

    for part in parts:
        await update.message.reply_text(part)
