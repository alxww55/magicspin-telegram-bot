from app.database.models import async_session
from app.database.models import AuthorizedUser, BlacklistedUser
from sqlalchemy import select, update, delete
from datetime import datetime


async def helper_get_user(model, user_id: int):
    async with async_session() as session:
        return await session.scalar(select(model).where(model.user_id == user_id))


async def add_user_to_authorized(user_id: int):
    async with async_session() as session:
        authorized_user = await helper_get_user(AuthorizedUser, user_id)

        if not authorized_user:
            session.add(AuthorizedUser(user_id=user_id,
                        coins=1000, timestamp=datetime.now()))

        await session.commit()


async def update_user_coins(user_id: int, coins: int):
    async with async_session() as session:
        authorized_user = await helper_get_user(AuthorizedUser, user_id)

        if authorized_user:
            await session.execute(update(AuthorizedUser).where(AuthorizedUser.user_id == user_id).values(coins=coins))

        await session.commit()


async def get_user_from_authorized(user_id: int) -> bool:
    async with async_session() as session:
        return bool(await helper_get_user(AuthorizedUser, user_id))


async def add_user_to_blacklist(user_id: int):
    async with async_session() as session:
        blacklisted_user = helper_get_user(BlacklistedUser, user_id)

        if not blacklisted_user:
            session.add(BlacklistedUser(
                user_id=user_id, timestamp=datetime.now()))

        await session.commit()


async def get_user_from_blacklist(user_id: int):
    async with async_session() as session:
        return bool(await helper_get_user(BlacklistedUser, user_id))
