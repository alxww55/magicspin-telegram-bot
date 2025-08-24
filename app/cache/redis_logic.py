"""
Redis-based user session manager.

This module defines the UserSession class, which handles:
- Creating and initializing user sessions in Redis
- Storing and updating user authorization status
- Managing user coins
- Handling message rate limiting

All data is stored in Redis hashes with expiration.
"""

import os
from datetime import datetime
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

RATE_LIMITING_PERIOD = int(os.getenv("RATE_LIMITING_PERIOD"))

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)


class UserSession():
    '''User session manager for Redis.'''

    def __init__(self, user_id: int | None = None):
        '''Initialize session object.

        args:
            user_id (int | None): Telegram User ID
        '''
        self.user_id = int(user_id)

    async def ensure_session(self, authorized_user=None) -> None:
        '''Ensure a session existence.

        args:
            authorized_user (object | None): Database user object for initialization

        return:
            None
        '''
        exists = await redis_client.exists(f"user_session:{self.user_id}")
        if not exists:
            if authorized_user:
                await self.init_instance_from_db(authorized_user)
            else:
                await self.init_instance_from_scratch()

    async def touch(self) -> None:
        '''Refresh TTL'''
        await redis_client.hexpire(f"user_session:{self.user_id}", 1800, "id", "user_id", "authorized", "coins", "timestamp")

    async def init_instance_from_scratch(self) -> None:
        '''Create a new session with default values.'''
        await redis_client.hset(f"user_session:{self.user_id}", mapping={
            "id": await redis_client.hincrby(f"user_session:{self.user_id}", "id"),
            "user_id": self.user_id,
            "messages": 0,
            "authorized": 0,
            "coins": 1000,
            "timestamp": str(datetime.now())
        })
        await self.touch()

    async def init_instance_from_db(self, authorized_user) -> None:
        '''Initialize session from a database user object.

        args:
            authorized_user (object): User from database

        return:
            None
        '''
        await redis_client.hset(f"user_session:{self.user_id}", mapping={
            "id": authorized_user.id,
            "user_id": authorized_user.user_id,
            "messages": 0,
            "authorized": 1,
            "coins": authorized_user.coins,
            "timestamp": str(authorized_user.timestamp)
        })
        await self.touch()

    async def get_instance(self) -> dict:
        '''Get the current session data.

        return:
            dict: Session data from Redis
        '''
        return await redis_client.hgetall(f"user_session:{self.user_id}")

    async def handle_messages(self):
        '''Increment message counter.

        return:
            int: Current message count
        '''
        await redis_client.hexpire(f"user_session:{self.user_id}", RATE_LIMITING_PERIOD, "messages")
        value = await redis_client.hincrby(f"user_session:{self.user_id}", "messages")
        return int(value) if value else 0

    async def authorize_user(self) -> int:
        '''Mark user as authorized in session.'''
        await redis_client.hset(f"user_session:{self.user_id}", "authorized", "1")

    async def check_authorization_status(self):
        '''Check if user is authorized.

        return:
            int: 1 if authorized, 0 if not
        '''
        value = await redis_client.hget(f"user_session:{self.user_id}", "authorized")
        return int(value) if value else 0

    async def get_coins_qty(self) -> int:
        '''Get current coin balance.

        return:
            int: Number of coins
        '''
        await self.touch()
        value = await redis_client.hget(f"user_session:{self.user_id}", "coins")
        return int(value) if value else 0

    async def change_coins_qty(self, coins_amount: int) -> None:
        '''Update user's coin balance.

        args:
            coins_amount (int): New coin amount

        return:
            None
        '''
        await self.touch()
        await redis_client.hset(f"user_session:{self.user_id}", "coins", coins_amount)
