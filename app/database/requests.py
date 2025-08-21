from app.database.models import async_session
from app.database.models import UnauthorizedUser, AuthorizedUser
from sqlalchemy import select, update, delete
from datetime import datetime

async def register_unauthorized_users(user_id):
    async with async_session() as session:
        user = await session.scalar(select(UnauthorizedUser).where(UnauthorizedUser.user_id == user_id))

        if not user:
            session.add(UnauthorizedUser(user_id=user_id, timestamp=datetime.now()))
            await session.commit()

async def add_user_to_authorized(user_id):
    async with async_session() as session:
        unauthorized_user = await session.scalar(select(UnauthorizedUser).where(UnauthorizedUser.user_id == user_id))
        authorized_user = await session.scalar(select(AuthorizedUser).where(AuthorizedUser.user_id == user_id))

        if unauthorized_user:
            await session.delete(unauthorized_user)
        
        if not authorized_user:
            session.add(AuthorizedUser(user_id=user_id, coins=1000, timestamp=datetime.now()))
        
        await session.commit()

async def get_coins_by_user_id(user_id):
    async with async_session() as session:
        return await session.scalar(select(AuthorizedUser.coins).where(AuthorizedUser.user_id == user_id))
