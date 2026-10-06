<!-- AI_ROLES_2026_10_06 -->
## Действующие роли AI-агентов — 06.10.2026
Решение собственника: **Codex и Kimi Code — равноправные исполнители; Claude — независимый второй проверяющий и помощник**. Прочитать общий файл `/Users/bdg78mailgmail.com/.agents/AGENTS.md` и проектный `AGENTS.md`. Эти роли заменяют прежние назначения исполнителя и аудитора в старых инструкциях; проектные факты, технические ограничения, согласования, проверки и история сохраняются. Инструкции исполнения ниже адресованы Codex/Kimi; Claude использует их для проверки и не получает разрешения изменять рабочие файлы или Git.

# NGO Bot — Бот НКО Потенциал

## Проект
AI-помощник для родителей детей с ОВЗ (@special_kids_benefits_bot).
Помогает с льготами, выплатами, оформлением ИППСУ — 24/7.
Мигрирован с n8n cloud (21 воркфлоу) в Python.

## Структура
```
bot.py              — точка входа (polling)
config.py           — загрузка .env
scheduler.py        — планировщик (news, digest, legislation)
handlers/           — обработчики Telegram (команды, текст, голос, кнопки)
services/           — AI-сервисы (Perplexity, Claude, Whisper, PDF, Email)
monitoring/         — мониторинг новостей и законодательства
webapp/             — Mini App webhook + статика
miniapp/            — Telegram Mini App (HTML/CSS/JS)
data/               — keywords.json (быстрые ответы)
```

## Запуск
```bash
pip3 install -r requirements.txt --break-system-packages
cp .env.example .env  # заполнить токены
python bot.py
```

## Ключевые API
- Perplexity (через OpenRouter) — поиск льгот
- Claude API — сложные консультации
- OpenAI Whisper — транскрипция голоса

## Безопасность
- Секреты только в .env (в .gitignore)
- Никогда не коммитить токены

## GitHub
- Репозиторий: bdg78mail/ngo-bot
