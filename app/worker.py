"""
Background task to synchronize user coin balances from Redis to the database.

This module defines an async function that:
- Periodically retrieves all user sessions from Redis.
- Ensures consistency between cache and database.
"""

import asyncio
from app.cache.redis_logic import redis_client, UserSession
import app.database.requests as rq


async def push_all_users_to_db():
    """
    Continuously push all user coin balances from Redis to the database.

    - Runs indefinitely with a 60-second interval between updates.

    """
    await asyncio.sleep(10)
    while True:
        keys = await redis_client.keys("user_session:*")
        for key in keys:
            user_id = int(key.split(":")[1])
            session = UserSession(user_id)
            coins = await session.get_coins_qty()
            if coins is not None:
                await rq.update_user_coins(user_id, coins)
            else:
                user_form_db = await rq.get_user_from_authorized(user_id)
                coins = user_form_db.coins
                await session.change_coins_qty(coins)
        await asyncio.sleep(60)
