"""
Web-сервер для Mini App:
- POST /api/webapp — webhook от Mini App
- GET / — статика Mini App (HTML/CSS/JS)
"""

import logging
import json
import os
from aiohttp import web

from config import WEBAPP_PORT
from handlers.miniapp import process_miniapp_request

log = logging.getLogger("ngo_bot.webapp")

MINIAPP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "miniapp")


async def handle_webapp_post(request):
    """POST /api/webapp — обработка запроса от Mini App."""
    try:
        data = await request.json()
        log.info(f"Mini App POST: {json.dumps(data, ensure_ascii=False)[:200]}")

        result = await process_miniapp_request(data)

        return web.json_response(result)

    except json.JSONDecodeError:
        return web.json_response(
            {"status": "error", "message": "Invalid JSON"},
            status=400,
        )
    except Exception as e:
        log.error(f"Ошибка webapp: {e}")
        return web.json_response(
            {"status": "error", "message": str(e)},
            status=500,
        )


async def handle_webapp_get(request):
    """GET / — отдаём Mini App (index.html)."""
    index_path = os.path.join(MINIAPP_DIR, "index.html")
    if os.path.exists(index_path):
        return web.FileResponse(index_path)
    return web.Response(text="Mini App not configured", status=404)


def create_webapp() -> web.Application:
    """Создать aiohttp-приложение для Mini App."""
    app = web.Application()

    # API endpoint
    app.router.add_post("/api/webapp", handle_webapp_post)

    # Статика Mini App
    if os.path.isdir(MINIAPP_DIR):
        app.router.add_static("/", MINIAPP_DIR)
    else:
        app.router.add_get("/", handle_webapp_get)

    return app


async def start_webapp():
    """Запуск веб-сервера."""
    app = create_webapp()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
    await site.start()
    log.info(f"Mini App веб-сервер запущен на порту {WEBAPP_PORT}")
    return runner
