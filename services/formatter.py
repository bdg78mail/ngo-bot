"""
Форматирование AI-ответов (Markdown → Telegram HTML).
Perplexity и Claude возвращают Markdown — конвертируем в HTML для Telegram.
"""

import re


def md_to_telegram_html(text: str) -> str:
    """
    Конвертация Markdown → Telegram HTML.

    Поддерживает: заголовки, жирный, курсив, списки, ссылки.
    Убирает: сноски Perplexity [1][2], горизонтальные линии.
    """
    # 1. Экранируем HTML-спецсимволы
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    # 2. Убираем сноски Perplexity: [1], [2][3], [1][2][3][4] и т.д.
    text = re.sub(r"(\[\d+\])+", "", text)

    # 3. Обрабатываем построчно
    lines = text.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()

        # Горизонтальные линии → пустая строка
        if re.match(r"^-{3,}$", stripped) or re.match(r"^\*{3,}$", stripped):
            result.append("")
            continue

        # Заголовки: #### → <b>
        heading_match = re.match(r"^#{1,6}\s+(.+)$", stripped)
        if heading_match:
            title = heading_match.group(1).strip()
            title = _inline_format(title)
            result.append(f"\n<b>{title}</b>")
            continue

        # Цитаты: > текст → текст
        if stripped.startswith("&gt; "):
            stripped = stripped[5:]
        elif stripped.startswith("&gt;"):
            stripped = stripped[4:]

        # Маркированные списки: - пункт → • пункт
        list_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if list_match:
            content = _inline_format(list_match.group(1))
            result.append(f"  • {content}")
            continue

        # Обычная строка — инлайн-форматирование
        result.append(_inline_format(stripped))

    text = "\n".join(result)

    # 4. Убираем лишние пустые строки (не более 2 подряд)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 5. Убираем пустые строки в начале/конце
    text = text.strip()

    return text


def _inline_format(text: str) -> str:
    """Инлайн-форматирование: жирный, курсив, ссылки."""
    # Ссылки: [текст](url) → <a href="url">текст</a>
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )

    # Жирный + курсив: ***текст*** → <b><i>текст</i></b>
    text = re.sub(r"\*{3}(.+?)\*{3}", r"<b><i>\1</i></b>", text)

    # Жирный: **текст** → <b>текст</b>
    text = re.sub(r"\*{2}(.+?)\*{2}", r"<b>\1</b>", text)

    # Курсив: *текст* → <i>текст</i> (но не внутри слов)
    text = re.sub(r"(?<!\w)\*([^*]+?)\*(?!\w)", r"<i>\1</i>", text)

    # Инлайн-код: `код` → <code>код</code>
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    return text
