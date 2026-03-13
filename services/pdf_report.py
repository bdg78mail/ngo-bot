"""
Генерация PDF-отчётов по льготам.
Использует reportlab для создания документов.
"""

import logging
import tempfile
import os
from datetime import datetime

from services.perplexity import search_benefits

log = logging.getLogger("ngo_bot.pdf_report")


async def generate_and_send_pdf(update, context, query: str):
    """
    Сгенерировать PDF-отчёт и отправить пользователю.

    Args:
        update: Telegram update
        context: Telegram context
        query: тема отчёта
    """
    try:
        # Собираем информацию
        content = await search_benefits(
            f"Подробный отчёт: {query}. "
            "Структурируй по разделам: федеральные льготы, региональные льготы, "
            "необходимые документы, куда обращаться, полезные контакты."
        )

        # Генерируем PDF
        pdf_path = await _create_pdf(query, content)

        if pdf_path:
            # Отправляем файл
            with open(pdf_path, "rb") as pdf_file:
                await update.message.reply_document(
                    document=pdf_file,
                    filename=f"отчёт_льготы_{datetime.now().strftime('%Y%m%d')}.pdf",
                    caption="Ваш отчёт готов! Информация актуальна на момент запроса.",
                )
            # Удаляем временный файл
            os.unlink(pdf_path)
        else:
            await update.message.reply_text(
                "Не удалось сгенерировать PDF. Отправляю текстом:\n\n" + content[:4000]
            )
    except Exception as e:
        log.error(f"Ошибка генерации PDF: {e}")
        await update.message.reply_text("Произошла ошибка при генерации отчёта. Попробуйте позже.")


async def _create_pdf(title: str, content: str) -> str | None:
    """
    Создать PDF-файл.

    Returns:
        Путь к PDF-файлу или None
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Временный файл
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp_path = tmp.name
        tmp.close()

        doc = SimpleDocTemplate(tmp_path, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()

        # Создаём стили (используем стандартный шрифт для кириллицы)
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=12,
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=6,
        )

        elements = []

        # Заголовок
        elements.append(Paragraph(f"НКО «Потенциал» — Отчёт", title_style))
        elements.append(Paragraph(f"Тема: {title}", body_style))
        elements.append(Paragraph(
            f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            body_style,
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Содержимое — разбиваем по строкам
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 0.3*cm))
            else:
                # Экранируем HTML-символы для reportlab
                line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                elements.append(Paragraph(line, body_style))

        # Дисклеймер
        elements.append(Spacer(1, 1*cm))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor='gray',
        )
        elements.append(Paragraph(
            "Данный отчёт носит информационный характер и не является юридической консультацией. "
            "Для принятия важных решений обратитесь к квалифицированному специалисту.",
            disclaimer_style,
        ))

        doc.build(elements)
        log.info(f"PDF создан: {tmp_path}")
        return tmp_path

    except ImportError:
        log.error("reportlab не установлен: pip3 install reportlab")
        return None
    except Exception as e:
        log.error(f"Ошибка создания PDF: {e}")
        return None
