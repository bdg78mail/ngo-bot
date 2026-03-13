"""
Сохранение обратной связи от пользователей.
"""

import logging
import json
import os
from datetime import datetime
from telegram import Update

from config import ADMIN_CHAT_ID

log = logging.getLogger("ngo_bot.feedback")

FEEDBACK_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "feedback.json")


async def save_user_feedback(update: Update, text: str):
    """
    Сохранить обратную связь и уведомить админа.

    Args:
        update: Telegram update
        text: текст обратной связи
    """
    user = update.effective_user
    feedback = {
        "user_id": user.id,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "text": text,
        "date": datetime.now().isoformat(),
    }

    # Сохраняем в файл
    _save_to_file(feedback)

    # Благодарим пользователя
    await update.message.reply_text(
        "Спасибо за обратную связь! Мы обязательно её учтём."
    )

    # Уведомляем админа
    if ADMIN_CHAT_ID:
        try:
            await update.get_bot().send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    f"<b>Новый отзыв</b>\n\n"
                    f"От: {user.first_name} (@{user.username or 'нет'})\n"
                    f"Текст: {text[:500]}"
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            log.error(f"Ошибка уведомления админа: {e}")

    log.info(f"Фидбек от {user.first_name}: {text[:80]}")


def _save_to_file(feedback: dict):
    """Сохранить фидбек в JSON-файл."""
    try:
        feedbacks = []
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                feedbacks = json.load(f)

        feedbacks.append(feedback)

        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

    except Exception as e:
        log.error(f"Ошибка сохранения фидбека: {e}")
