import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.db.database import engine
from bot.db.models import Base
from bot.handlers import converter, start
from bot.loader import redis
from bot.middlewares.db_middleware import DbSessionMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
log = logging.getLogger(__name__)


async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables ready")


async def on_shutdown():
    await redis.aclose()
    await engine.dispose()
    log.info("Shutdown complete")


async def main():
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.message.middleware(DbSessionMiddleware())

    dp.include_router(start.router)
    dp.include_router(converter.router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    log.info("Bot starting…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
