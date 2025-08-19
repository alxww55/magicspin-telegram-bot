import asyncio
import redis.asyncio as redis
import os
from dotenv import load_dotenv

import app.database.requests as rq

load_dotenv()

async def calculate_login_attempts(id: int):
    async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
        await redis_conn.incr(id)

async def get_cached_attempts(id: int):
    async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
        return await redis_conn.get(id)
    
async def clear_login_attempts(id: int): 
    async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
        await redis_conn.delete(id)

async def load_coins_into_cache(id: int):
    async with redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True) as redis_conn:
        return await redis_conn.set("user_coins", rq.get_coins_by_user_id(id))