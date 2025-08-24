import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from loguru import logger

from app.handlers import router
from app.database.models import async_main
from app.worker import push_all_users_to_db

logger.add("logs/log.log", rotation="1 day", level="INFO", enqueue=True)

async def main():
    """
    Main function, does following:
    - Creates all tables in the database if they do not exist.
    - Initializes bot and bot instance
    - Includes router and starts polling
    """
    logger.info("Loading environment variables...")
    load_dotenv()
    logger.info("Creating database tables...")
    await async_main()
    logger.info("Starting sync between cache and database...")
    asyncio.create_task(push_all_users_to_db())
    logger.info("Initializing and starting bot")
    bot = Bot(token=os.getenv("BOT_API_KEY"))
    dp = Dispatcher()
    dp.include_router(router)
    try:
        logger.info("Bot started")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopped")
