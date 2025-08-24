"""
Database helper functions for managing authorized and blacklisted users.

This module provides async functions to interact with the database:
- Add, update, and fetch authorized users
- Manage user coins
- Move users to blacklist and check blacklist status

All functions use SQLAlchemy async sessions.
"""

from app.database.models import async_session
from app.database.models import AuthorizedUser, BlacklistedUser
from sqlalchemy import select, update, delete
from datetime import datetime


async def helper_get_user(model, user_id: int) -> object:
    '''Fetch a user from the database by model and user_id.

    args:
        model: SQLAlchemy model (AuthorizedUser or BlacklistedUser).
        user_id (int): Telegram User ID.

    return:
        User object if found, otherwise None
    '''
    async with async_session() as session:
        return await session.scalar(select(model).where(model.user_id == user_id))


async def add_user_to_authorized(user_id: int) -> None:
    '''Add a user to authorized list with default coins.

    args:
        user_id (int): Telegram User ID

    return:
        None
    '''
    async with async_session() as session:
        authorized_user = await helper_get_user(AuthorizedUser, user_id)
        if not authorized_user:
            session.add(AuthorizedUser(user_id=user_id,
                        coins=1000, timestamp=datetime.now()))
        await session.commit()


async def update_user_coins(user_id: int, coins: int) -> None:
    '''Update coin balance for an authorized user.

    args:
        user_id (int): Telegram User ID
        coins (int): New coin amount

    return:
        None
    '''
    async with async_session() as session:
        authorized_user = await helper_get_user(AuthorizedUser, user_id)
        if authorized_user:
            await session.execute(update(AuthorizedUser).where(AuthorizedUser.user_id == user_id).values(coins=coins))
        await session.commit()


async def get_user_from_authorized(user_id: int) -> AuthorizedUser | None:
    '''Get authorized user by ID.

    args:
        user_id (int): Telegram User ID

    return:
        AuthorizedUser object if found, otherwise None
    '''
    return await helper_get_user(AuthorizedUser, user_id)


async def add_user_to_blacklist(user_id: int) -> None:
    '''Add a user to blacklist and remove from authorized if exists.

    args:
        user_id (int): Telegram User ID

    return:
        None
    '''
    async with async_session() as session:
        blacklisted_user = await helper_get_user(BlacklistedUser, user_id)
        authorized_user = await helper_get_user(AuthorizedUser, user_id)

        if authorized_user:
            await session.execute(delete(AuthorizedUser).where(AuthorizedUser.user_id == user_id))

        if not blacklisted_user:
            session.add(BlacklistedUser(
                user_id=user_id, timestamp=datetime.now()))
        await session.commit()


async def get_user_from_blacklist(user_id: int):
    '''Check if a user is in the blacklist.

    args:
        user_id (int): Telegram User ID

    return:
        bool: True if in blacklist, False otherwise
    '''
    return bool(await helper_get_user(BlacklistedUser, user_id))
