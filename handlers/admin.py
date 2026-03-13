"""
Обработка админских одобрений.
Админ может одобрять/отклонять контент перед публикацией.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import ADMIN_CHAT_ID

log = logging.getLogger("ngo_bot.admin")


def is_admin(chat_id: int | str) -> bool:
    """Проверка, является ли пользователь админом."""
    return str(chat_id) == str(ADMIN_CHAT_ID)


async def send_for_approval(bot, text: str, approval_id: str):
    """
    Отправить контент админу на одобрение.

    Args:
        bot: объект бота
        text: текст для одобрения
        approval_id: уникальный ID для отслеживания
    """
    if not ADMIN_CHAT_ID:
        log.warning("ADMIN_CHAT_ID не задан")
        return

    keyboard = [
        [
            InlineKeyboardButton("Одобрить", callback_data=f"approve_{approval_id}"),
            InlineKeyboardButton("Отклонить", callback_data=f"reject_{approval_id}"),
        ],
    ]

    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"<b>На одобрение:</b>\n\n{text[:3000]}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_admin_callback(query, context, action: str, approval_id: str):
    """
    Обработка решения админа.

    Args:
        query: callback query
        context: контекст бота
        action: "approve" или "reject"
        approval_id: ID одобрения
    """
    if not is_admin(query.from_user.id):
        await query.answer("У вас нет прав администратора.", show_alert=True)
        return

    if action == "approve":
        await query.edit_message_text(f"Одобрено ({approval_id})")
        log.info(f"Контент {approval_id} одобрен админом")
    else:
        await query.edit_message_text(f"Отклонено ({approval_id})")
        log.info(f"Контент {approval_id} отклонён админом")
