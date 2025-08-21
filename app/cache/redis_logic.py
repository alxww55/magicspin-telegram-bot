import os
from datetime import datetime
import redis.asyncio as redis
from dotenv import load_dotenv


load_dotenv()


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True
)


class UserSession():

    def __init__(self, user_id: int | None = None):
        self.user_id = user_id

    async def init_instance(self):
        exists = await redis_client.exists(f"user_session:{self.user_id}")
        if not exists:
            await redis_client.hset(f"user_session:{self.user_id}", mapping={
                "id": await redis_client.hincrby(f"user_session:{self.user_id}", "id"),
                "user_id": self.user_id,
                "messages": 0,
                "authorized": 0,
                "coins": 1000,
                "timestamp": str(datetime.now())
            })
        await redis_client.hexpire(f"user_session:{self.user_id}", 3600, "id, user_id, authorized, coins, timestamp")

    async def handle_messages(self):
        await redis_client.hexpire(f"user_session:{self.user_id}", 30, "messages")
        return int(await redis_client.hincrby(f"user_session:{self.user_id}", "messages"))

    async def authorize_user(self):
        await redis_client.hset(f"user_session:{self.user_id}", "authorized", "1")

    async def check_authorization_status(self):
        return int(await redis_client.hget(f"user_session:{self.user_id}", "authorized"))

    async def get_coins_qty(self):
        return int(await redis_client.hget(f"user_session:{self.user_id}", "coins"))

    async def change_coins_qty(self, coins_amount: int):
        await redis_client.hset(f"user_session:{self.user_id}", "coins", coins_amount)
