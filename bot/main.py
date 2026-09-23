"""
main.py — Bot entry point.

Supports both polling (local dev) and webhook (Railway/cloud) modes.
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.config import load_config
from bot.database import init_db
from bot.handlers import business, connection, deleted, edited, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, config, dp: Dispatcher) -> None:
    """Actions on bot startup."""
    # Initialize DB
    os.makedirs(os.path.dirname(config.db_path) or "data", exist_ok=True)
    await init_db(config.db_path)
    logger.info("Database initialized: %s", config.db_path)

    if config.webhook_url:
        await bot.set_webhook(config.webhook_url)
        logger.info("Webhook set: %s", config.webhook_url)
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Running in polling mode")

    # Notify all configured owners that bot started
    try:
        me = await bot.get_me()
        startup_text = (
            f"✅ <b>Bot ishga tushdi!</b>\n\n"
            f"🤖 <code>@{me.username}</code>\n"
            f"📋 Mode: {'Webhook' if config.webhook_url else 'Polling'}\n\n"
            "Endi chatlaringizni kuzatishim mumkin!"
        )
        for owner_id in config.owner_ids:
            try:
                await bot.send_message(
                    owner_id,
                    startup_text,
                    parse_mode="HTML",
                )
            except Exception as ex:
                logger.warning("Could not send startup message to %s: %s", owner_id, ex)
    except Exception as e:
        logger.warning("Could not send startup message: %s", e)


async def on_shutdown(bot: Bot, config) -> None:
    """Actions on bot shutdown."""
    if config.webhook_url:
        await bot.delete_webhook()
    logger.info("Bot stopped")


def create_dispatcher(config) -> Dispatcher:
    """Build and configure the dispatcher."""
    dp = Dispatcher()

    # Inject config into all handlers via middleware data
    dp["config"] = config

    # Register routers
    dp.include_router(start.router)
    dp.include_router(connection.router)
    dp.include_router(business.router)
    dp.include_router(deleted.router)
    dp.include_router(edited.router)

    return dp


async def run_polling(bot: Bot, dp: Dispatcher, config) -> None:
    """Run bot in long-polling mode (with health check port for Render/cloud)."""
    await on_startup(bot, config, dp)

    runner = None
    if config.webhook_port:
        try:
            app = web.Application()

            async def health(_req):
                return web.Response(text="Bot is running (polling mode)!")

            app.router.add_get("/", health)
            app.router.add_get("/health", health)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host="0.0.0.0", port=config.webhook_port)
            await site.start()
            logger.info("Health check server listening on port %s", config.webhook_port)
        except Exception as e:
            logger.warning("Could not start health check server: %s", e)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        if runner:
            await runner.cleanup()
        await on_shutdown(bot, config)


def run_webhook(bot: Bot, dp: Dispatcher, config) -> None:
    """Run bot in webhook mode (for Railway/cloud)."""
    app = web.Application()

    async def startup(_app):
        await on_startup(bot, config, dp)

    async def shutdown(_app):
        await on_shutdown(bot, config)

    app.on_startup.append(startup)
    app.on_shutdown.append(shutdown)

    # Health check endpoints for Render/cloud platforms
    async def health_check(_request):
        return web.Response(text="Bot is running!")

    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=config.webhook_port)


def main() -> None:
    config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher(config)

    if config.webhook_url:
        logger.info("Starting in webhook mode on port %s", config.webhook_port)
        run_webhook(bot, dp, config)
    else:
        logger.info("Starting in polling mode (local dev)")
        asyncio.run(run_polling(bot, dp, config))


if __name__ == "__main__":
    main()
