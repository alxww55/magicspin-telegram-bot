"""
Custom Aiogram middleware for user rate limiting and registration.

This module provides:
- RateLimiter: Limits the number of messages or callbacks a user can send within a time period. Blacklists users who exceed the limit.
- RegisterUser: Ensures that users are registered in the session and authorized in the database.
"""

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
    """
    Middleware to limit the number of messages/callbacks a user can send.

    - Checks if the user is blacklisted.
    - Limits messages per MESSAGES_PER_PERIOD.
    - Adds users to blacklist if limit exceeded.
    """
    async def __call__(self, handler, event, data) -> Callable | None:
        """
        Check and enforce message rate limits for the user.

        Args:
            handler (Callable): The next handler in the middleware chain.
            event (TelegramObject): Incoming Telegram event (Message or CallbackQuery).
            data (Dict[str, Any]): Additional data passed to the handler.

        Returns:
            Callable | None: Executes the handler if user is within limits, otherwise None.
        """
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
    """
    Middleware to register users in the session and database.

    - Checks if user is authorized on every event
    - Ensures the user's session exists.
    - Adds user to authorized users if not already present.
    """
    async def __call__(self, handler, event, data) -> Callable | None:
        """
        Register the user and ensure authorization status.

        Args:
            handler (Callable): The next handler in the middleware chain.
            event (TelegramObject): Incoming Telegram event (Message or CallbackQuery).
            data (Dict[str, Any]): Additional data passed to the handler.

        Returns:
            Callable | None: Executes the handler after ensuring registration.
        """
        session = UserSession(event.from_user.id)
        await session.ensure_session()
        auth_status = await session.check_authorization_status()

        if auth_status:
            await db.add_user_to_authorized(event.from_user.id)

        return await handler(event, data)
