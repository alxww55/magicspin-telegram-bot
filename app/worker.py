import asyncio
from app.cache.redis_logic import redis_client, UserSession
import app.database.requests as rq  # твоя база


async def push_all_users_to_db():
    while True:
        keys = await redis_client.keys("user_session:*")
        for key in keys:
            user_id = int(key.split(":")[1])
            session = UserSession(user_id)
            coins = int(await session.get_coins_qty())
            await rq.update_user_coins(user_id, coins)
        await asyncio.sleep(60)
