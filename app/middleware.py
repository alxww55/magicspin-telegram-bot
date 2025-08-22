import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from app.cache.redis_logic import UserSession
import app.database.requests as db

load_dotenv()

MESSAGES_PER_PERIOD = int(os.getenv("MESSAGES_PER_PERIOD"))


class BaseMiddlware(ABC):
    @abstractmethod
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Callable | None:
        pass


class RateLimiter(BaseMiddlware):
    async def __call__(self, handler, event, data) -> Callable | None:

        is_blacklisted = await db.get_user_from_blacklist(event.from_user.id)
        if is_blacklisted:
            return

        user_in_db = await db.get_user_from_authorized(event.from_user.id)
        session = UserSession(event.from_user.id)

        await session.ensure_session(user_in_db)

        user_messages = await session.handle_messages()

        if isinstance(event, Message) and user_messages > MESSAGES_PER_PERIOD:
            if event.text and event.text.startswith("/start"):
                await event.answer("You were blocked! Please contact administrator!")
                await db.add_user_to_blacklist(event.from_user.id)

        if isinstance(event, CallbackQuery) and user_messages > MESSAGES_PER_PERIOD:
            await event.answer("You were blocked! Please contact administrator!")
            await db.add_user_to_blacklist(event.from_user.id)
            return

        return await handler(event, data)


class RegisterUser(BaseMiddlware):
    async def __call__(self, handler, event, data) -> Callable | None:

        session = UserSession(event.from_user.id)
        await session.ensure_session()
        auth_status = await session.check_authorization_status()

        if auth_status:
            await db.add_user_to_authorized(event.from_user.id)

        return await handler(event, data)
