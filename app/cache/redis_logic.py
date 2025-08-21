import os
import asyncio
from datetime import datetime
import redis.asyncio as redis
from dotenv import load_dotenv

import app.database.requests as rq

load_dotenv()


class UserSession():

    def __init__(self, user_id: int | None = None):
        self.user_id = user_id

    async def init_instance(self):
        async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
            exists = await redis_conn.exists(f"user_session:{self.user_id}")
            if not exists:
                await redis_conn.hset(f"user_session:{self.user_id}", mapping={
                    "id": await redis_conn.hincrby(f"user_session:{self.user_id}", "id"),
                    "user_id": self.user_id,
                    "login_attempts": 0,
                    "authorized": 0,
                    "coins": 1000,
                    "timestamp": str(datetime.now())
                })

    async def handle_login_attempts(self):
        async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
            await redis_conn.hincrby(f"user_session:{self.user_id}", "login_attempts")
            await redis_conn.hexpire(f"user_session:{self.user_id}", 600, "login_attempts")
            return await redis_conn.hget(f"user_session:{self.user_id}", "login_attempts")

    async def authorize_user(self):
        async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
            await redis_conn.hset(f"user_session:{self.user_id}", "authorized", "1")

    async def check_authorization_status(self):
        async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
            await redis_conn.hget(f"user_session:{self.user_id}", "authorized")

    async def get_coins_qty(self):
        async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
            return await redis_conn.hget(f"user_session:{self.user_id}", "coins")

    async def change_coins_qty(self, coins_amount: int):
        async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
            await redis_conn.hset(f"user_session:{self.user_id}", "coins", coins_amount)
