"""
Конфигурация бота НКО Потенциал.
Все секреты — в .env файле (не коммитится).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram бот (@special_kids_benefits_bot)
BOT_TOKEN = os.getenv("NGO_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

# AI-сервисы
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Модели
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "perplexity/sonar-pro")

# Режим работы
BOT_MODE = os.getenv("BOT_MODE", "polling")  # polling или webhook

# Mini App / Webhook
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8080"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# TTS (не приоритет)
YANDEX_TTS_API_KEY = os.getenv("YANDEX_TTS_API_KEY", "")
SBER_TTS_API_KEY = os.getenv("SBER_TTS_API_KEY", "")
