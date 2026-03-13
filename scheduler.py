"""
Планировщик фоновых задач:
- Ежедневный скан новостей (утро)
- Мониторинг законодательства (раз в день)
- Еженедельный дайджест (понедельник утро)
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from monitoring.news_scanner import scan_daily_news
from monitoring.relevance_analyzer import analyze_relevance
from monitoring.message_creator import create_messages
from monitoring.weekly_digest import create_weekly_digest
from monitoring.legislation_monitor import check_legislation_changes
from config import ADMIN_CHAT_ID

log = logging.getLogger("ngo_bot.scheduler")

# Хранилище новостей за неделю (в памяти; для продакшна — БД)
_weekly_news: list[dict] = []


async def daily_news_pipeline(bot=None):
    """
    Ежедневный pipeline: скан → анализ → сообщения → админу.
    """
    log.info("Запуск ежедневного pipeline новостей")

    # A: Скан новостей
    raw_news = await scan_daily_news()
    if not raw_news:
        log.info("Новостей не найдено")
        return

    # B: Анализ релевантности
    relevant = await analyze_relevance(raw_news)

    # C: Создание сообщений
    messages = await create_messages(relevant)

    # Сохраняем для дайджеста
    _weekly_news.extend(relevant)

    # Отправляем админу
    if bot and ADMIN_CHAT_ID and messages:
        for msg in messages[:3]:  # Максимум 3 сообщения в день
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"<b>Новость дня:</b>\n\n{msg}",
                    parse_mode="HTML",
                )
            except Exception as e:
                log.error(f"Ошибка отправки новости админу: {e}")

    log.info(f"Pipeline завершён: {len(messages)} сообщений")


async def daily_legislation_check(bot=None):
    """Ежедневная проверка законодательства."""
    log.info("Проверка законодательства")
    changes = await check_legislation_changes()

    if changes and bot and ADMIN_CHAT_ID:
        for change in changes[:2]:
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"<b>Законодательство:</b>\n\n{change['content'][:1000]}",
                    parse_mode="HTML",
                )
            except Exception as e:
                log.error(f"Ошибка отправки: {e}")


async def weekly_digest_send(bot=None):
    """Еженедельный дайджест."""
    global _weekly_news
    log.info("Формирование еженедельного дайджеста")

    digest = await create_weekly_digest(_weekly_news)

    if bot and ADMIN_CHAT_ID:
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=digest,
                parse_mode="HTML",
            )
        except Exception as e:
            log.error(f"Ошибка отправки дайджеста: {e}")

    # Очищаем новости за неделю
    _weekly_news = []


def setup_scheduler(bot=None) -> AsyncIOScheduler:
    """
    Настройка планировщика.

    Args:
        bot: объект бота Telegram (для отправки сообщений)

    Returns:
        Настроенный планировщик
    """
    scheduler = AsyncIOScheduler()

    # Ежедневный скан новостей — 8:00 МСК
    scheduler.add_job(
        daily_news_pipeline,
        "cron",
        hour=8,
        minute=0,
        kwargs={"bot": bot},
        id="daily_news",
    )

    # Проверка законодательства — 12:00 МСК
    scheduler.add_job(
        daily_legislation_check,
        "cron",
        hour=12,
        minute=0,
        kwargs={"bot": bot},
        id="legislation_check",
    )

    # Еженедельный дайджест — понедельник 9:00 МСК
    scheduler.add_job(
        weekly_digest_send,
        "cron",
        day_of_week="mon",
        hour=9,
        minute=0,
        kwargs={"bot": bot},
        id="weekly_digest",
    )

    log.info("Планировщик настроен: daily_news (8:00), legislation (12:00), digest (пн 9:00)")
    return scheduler
