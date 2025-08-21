from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from app.cache.redis_logic import redis_client, UserSession
import app.database.requests as db


class RateLimiter(BaseMiddleware):
    async def __call__(self,
                       handler=Callable[[TelegramObject,
                                         Dict[str, any]], Awaitable[Any]],
                       event=TelegramObject,
                       data=Dict[str, Any]) -> Callable | None:

        is_blacklisted = await db.get_user_from_blacklist(event.from_user.id)
        if is_blacklisted:
            return

        session = UserSession(event.from_user.id)
        await session.init_instance()
        user_messages = await session.handle_messages()

        if isinstance(event, Message) and user_messages > 30:
            if event.text and event.text.startswith("/start"):
                await event.answer("You were blocked! Please contact administrator!")
                await db.add_user_to_blacklist(event.from_user.id)

        if isinstance(event, CallbackQuery) and user_messages > 60:
            await event.answer("You were blocked! Please contact administrator!")
            await db.add_user_to_blacklist(event.from_user.id)
            return

        return await handler(event, data)


class RegisterUser(BaseMiddleware):
    async def __call__(self,
                       handler=Callable[[TelegramObject,
                                         Dict[str, any]], Awaitable[Any]],
                       event=CallbackQuery,
                       data=Dict[str, Any]) -> Callable | None:

        session = UserSession(event.from_user.id)
        await session.init_instance()
        auth_status = await session.check_authorization_status()

        if auth_status and int(auth_status):
            await db.add_user_to_authorized(event.from_user.id)

        return await handler(event, data)


# class PushToDB(BaseMiddleware):
#     async def __call__(self,
#                        handler=Callable[[TelegramObject,
#                                          Dict[str, any]], Awaitable[Any]],
#                        event=CallbackQuery,
#                        data=Dict[str, Any]) -> Callable | None:

#         session = UserSession(event.from_user.id)
#         await session.init_instance()
#         await db.update_user_coins(event.from_user.id, int(await session.get_coins_qty()))
#         return await handler(event, data)
