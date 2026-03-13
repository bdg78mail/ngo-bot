"""
Обработчики команд: /start, /help, /about, /share, /feedback.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

log = logging.getLogger("ngo_bot.commands")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start — главное меню с кнопками."""
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
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Здравствуйте! Я — AI-помощник НКО «Потенциал».\n\n"
        "Помогу разобраться с льготами и соцуслугами "
        "для семей с детьми с ОВЗ.\n\n"
        "Выберите действие или просто напишите ваш вопрос:",
        reply_markup=reply_markup,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help — подсказка для родителей."""
    await update.message.reply_text(
        "<b>Как пользоваться ботом:</b>\n\n"
        "Просто напишите ваш вопрос текстом или отправьте голосовое сообщение.\n\n"
        "<b>Примеры вопросов:</b>\n"
        "— Какие льготы положены ребёнку-инвалиду?\n"
        "— Как оформить ИППСУ?\n"
        "— Какие выплаты можно получить в 2026 году?\n"
        "— Какие программы поддержки есть в Свердловской области?\n\n"
        "<b>Команды:</b>\n"
        "/start — главное меню\n"
        "/help — эта справка\n"
        "/about — о боте\n"
        "/share — поделиться ботом\n"
        "/feedback — обратная связь\n\n"
        "<i>Если вопрос сложный, мне может потребоваться "
        "чуть больше времени на ответ.</i>",
        parse_mode="HTML",
    )


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/about — информация о боте и НКО."""
    await update.message.reply_text(
        "<b>О боте НКО «Потенциал»</b>\n\n"
        "Этот бот создан НКО «Потенциал» (Екатеринбург) "
        "для помощи семьям с детьми с ОВЗ.\n\n"
        "Бот использует искусственный интеллект для поиска "
        "актуальной информации о льготах, выплатах и "
        "социальных услугах.\n\n"
        "<b>Что умеет бот:</b>\n"
        "— Поиск льгот по региону, возрасту, категории\n"
        "— Персональные консультации\n"
        "— Генерация PDF-отчётов\n"
        "— Мониторинг изменений законодательства\n"
        "— Еженедельный дайджест новостей\n\n"
        "<i>Бот не заменяет юридическую консультацию. "
        "Для принятия важных решений обратитесь к специалисту.</i>",
        parse_mode="HTML",
    )


async def cmd_share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/share — поделиться ботом."""
    await update.message.reply_text(
        "Поделитесь ботом с другими родителями!\n\n"
        "Ссылка: https://t.me/special_kids_benefits_bot\n\n"
        "Бот бесплатный и работает 24/7.",
    )


async def cmd_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/feedback — обратная связь."""
    # Устанавливаем флаг ожидания фидбека
    context.user_data["awaiting_feedback"] = True
    await update.message.reply_text(
        "Напишите ваш отзыв или предложение.\n"
        "Мы обязательно его прочитаем!",
    )
