"""
Обработка InlineKeyboard callback_query.
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.tts import synthesize

log = logging.getLogger("ngo_bot.callbacks")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Роутер callback-кнопок."""
    query = update.callback_query
    await query.answer()

    data = query.data
    log.info(f"Callback: {data}")

    handlers = {
        "ask_benefits": _ask_benefits,
        "consultation": _consultation,
        "program_search": _program_search,
        "pdf_report": _pdf_report,
        "about": _about,
        "feedback": _feedback,
        "back_to_menu": _back_to_menu,
        "tts_listen": _tts_listen,
    }

    handler = handlers.get(data)
    if handler:
        await handler(query, context)
    else:
        await query.edit_message_text(f"Неизвестная команда: {data}")


async def _ask_benefits(query, context):
    """Кнопка «Задать вопрос о льготах»."""
    await query.edit_message_text(
        "Напишите ваш вопрос о льготах, и я найду актуальную информацию.\n\n"
        "Например:\n"
        "— Какие выплаты положены ребёнку-инвалиду в 2026?\n"
        "— Как получить бесплатные лекарства?\n"
        "— Какие льготы при поступлении в школу?",
    )


async def _consultation(query, context):
    """Кнопка «Консультация»."""
    await query.edit_message_text(
        "Для персональной консультации опишите вашу ситуацию подробно:\n\n"
        "— Регион проживания\n"
        "— Возраст ребёнка\n"
        "— Категория инвалидности (если есть)\n"
        "— Ваш конкретный вопрос\n\n"
        "Чем больше деталей, тем точнее будет ответ.",
    )
    context.user_data["mode"] = "consultation"


async def _program_search(query, context):
    """Кнопка «Поиск программ»."""
    keyboard = [
        [InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")],
    ]
    await query.edit_message_text(
        "Напишите, какие программы поддержки вас интересуют.\n\n"
        "Я найду подходящие программы и могу отправить результат на email.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    context.user_data["mode"] = "program_search"


async def _pdf_report(query, context):
    """Кнопка «PDF-отчёт»."""
    keyboard = [
        [InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")],
    ]
    await query.edit_message_text(
        "Опишите тему для PDF-отчёта.\n\n"
        "Например: «Все льготы для ребёнка-инвалида в Свердловской области»\n\n"
        "Я соберу информацию и пришлю вам готовый документ.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    context.user_data["mode"] = "pdf_report"


async def _about(query, context):
    """Кнопка «О боте»."""
    keyboard = [
        [InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")],
    ]
    await query.edit_message_text(
        "<b>О боте НКО «Потенциал»</b>\n\n"
        "Создан для помощи семьям с детьми с ОВЗ.\n"
        "Использует ИИ для поиска актуальной информации о льготах.\n\n"
        "<i>Не заменяет юридическую консультацию.</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def _feedback(query, context):
    """Кнопка «Обратная связь»."""
    context.user_data["awaiting_feedback"] = True
    await query.edit_message_text(
        "Напишите ваш отзыв или предложение.\n"
        "Мы обязательно его прочитаем!",
    )


async def _back_to_menu(query, context):
    """Вернуться в главное меню."""
    keyboard = [
        [
            InlineKeyboardButton("Задать вопрос о льготах", callback_data="ask_benefits"),
            InlineKeyboardButton("Консультация", callback_data="consultation"),
        ],
        [
            InlineKeyboardButton("Поиск программ", callback_data="program_search"),
            InlineKeyboardButton("PDF-отчёт", callback_data="pdf_report"),
        ],
        [
            InlineKeyboardButton("О боте", callback_data="about"),
            InlineKeyboardButton("Обратная связь", callback_data="feedback"),
        ],
    ]
    await query.edit_message_text(
        "Выберите действие или просто напишите ваш вопрос:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def _tts_listen(query, context):
    """Кнопка «Прослушать» — озвучка последнего ответа."""
    text = context.chat_data.get("last_answer", "")

    if not text:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Нет текста для озвучки.")
        return

    # Показываем что генерируем аудио
    await query.answer("Генерирую аудио...")
    chat_id = query.message.chat_id
    await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")

    # Генерируем TTS
    audio_path = await synthesize(text)

    if audio_path:
        try:
            with open(audio_path, "rb") as audio_file:
                await context.bot.send_voice(
                    chat_id=chat_id,
                    voice=audio_file,
                )
        finally:
            # Удаляем временный файл
            try:
                os.unlink(audio_path)
            except OSError:
                pass
    else:
        await query.message.reply_text("Не удалось сгенерировать аудио. Попробуйте позже.")
