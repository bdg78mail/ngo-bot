"""
Отправка email с результатами и отчётами.
"""

import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

log = logging.getLogger("ngo_bot.email")


async def send_email(
    to: str,
    subject: str,
    body: str,
    attachment_path: str = "",
    attachment_name: str = "",
) -> bool:
    """
    Отправить email.

    Args:
        to: адрес получателя
        subject: тема письма
        body: текст письма
        attachment_path: путь к вложению (опционально)
        attachment_name: имя файла вложения (опционально)

    Returns:
        True если отправлено успешно
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        log.error("SMTP не настроен (SMTP_USER / SMTP_PASSWORD)")
        return False

    try:
        import aiosmtplib

        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html", "utf-8"))

        # Вложение
        if attachment_path:
            with open(attachment_path, "rb") as f:
                att = MIMEApplication(f.read())
                att.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=attachment_name or "report.pdf",
                )
                msg.attach(att)

        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=False,
            start_tls=True,
        )
        log.info(f"Email отправлен: {to}")
        return True

    except ImportError:
        log.error("aiosmtplib не установлен: pip3 install aiosmtplib")
        return False
    except Exception as e:
        log.error(f"Ошибка отправки email: {e}")
        return False
