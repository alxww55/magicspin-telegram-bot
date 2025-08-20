import os
import asyncio
import redis.asyncio as redis
from dotenv import load_dotenv

import app.database.requests as rq

load_dotenv()

# redis_instance =  

async def handle_login_attempts(id: int):
    async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
        key = str(id) + "_" + "login"
        await redis_conn.incr(key)
        await redis_conn.expire(key, 600)
        return await redis_conn.get(key)

async def get_coins_qty(id: int):
    async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
        key = str(id) + "_" + "user_coins"
        value = await redis_conn.get(key)
        
        if not value:
            coins = await rq.get_coins_by_user_id(id)
            await redis_conn.set(id, coins)
            return coins
        
        return value

async def change_coins_qty(id: int, coins_amount: int):
    async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
        key = str(id) + "_" + "user_coins"
        await redis_conn.set(key, coins_amount)