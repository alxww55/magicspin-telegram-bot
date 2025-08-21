import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from app.handlers import router
from app.database.models import async_main
from app.worker import push_all_users_to_db

async def main():
    await async_main()
    asyncio.create_task(push_all_users_to_db())
    load_dotenv()
    bot = Bot(token=os.getenv("BOT_API_KEY"))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[!] Bot stopped")
