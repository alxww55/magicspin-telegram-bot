import os
from datetime import datetime
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

RATE_LIMITING_PERIOD = int(os.getenv("RATE_LIMITING_PERIOD"))

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)


class UserSession():

    def __init__(self, user_id: int | None = None):
        self.user_id = int(user_id)

    async def ensure_session(self, authorized_user=None):
        exists = await redis_client.exists(f"user_session:{self.user_id}")
        if not exists:
            if authorized_user:
                await self.init_instance_from_db(authorized_user)
            else:
                await self.init_instance_from_scratch()

    async def touch(self):
        await redis_client.hexpire(f"user_session:{self.user_id}", 1800, "id", "user_id", "authorized", "coins", "timestamp")

    async def init_instance_from_scratch(self):
        await redis_client.hset(f"user_session:{self.user_id}", mapping={
            "id": await redis_client.hincrby(f"user_session:{self.user_id}", "id"),
            "user_id": self.user_id,
            "messages": 0,
            "authorized": 0,
            "coins": 1000,
            "timestamp": str(datetime.now())
        })
        await self.touch()

    async def init_instance_from_db(self, authorized_user):
        await redis_client.hset(f"user_session:{self.user_id}", mapping={
            "id": authorized_user.id,
            "user_id": authorized_user.user_id,
            "messages": 0,
            "authorized": 1,
            "coins": authorized_user.coins,
            "timestamp": str(authorized_user.timestamp)
        })
        await self.touch()

    async def get_instance(self):
        return await redis_client.hgetall(f"user_session:{self.user_id}")

    async def handle_messages(self):
        await redis_client.hexpire(f"user_session:{self.user_id}", RATE_LIMITING_PERIOD, "messages")
        value = await redis_client.hincrby(f"user_session:{self.user_id}", "messages")
        return int(value) if value else 0

    async def authorize_user(self):
        await redis_client.hset(f"user_session:{self.user_id}", "authorized", "1")

    async def check_authorization_status(self):
        value = await redis_client.hget(f"user_session:{self.user_id}", "authorized")
        return int(value) if value else 0

    async def get_coins_qty(self):
        await self.touch()
        value = await redis_client.hget(f"user_session:{self.user_id}", "coins")
        return int(value) if value else 0

    async def change_coins_qty(self, coins_amount: int):
        await self.touch()
        await redis_client.hset(f"user_session:{self.user_id}", "coins", coins_amount)
