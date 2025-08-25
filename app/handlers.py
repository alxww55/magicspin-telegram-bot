"""
Telegram slot machine bot handlers using Aiogram.

This module defines:
- Message and callback query handlers for Magic Spin slot machine simulator.
- Captcha-based user authorization.
- Slot machine spin logic, coin management, and profile display.
- Bid selection, coin top-up, and rules display.

All handlers are async and use FSMContext for user states, and Redis-based UserSession for coin storage.
"""

import asyncio
from aiogram import F, Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.types.error_event import ErrorEvent
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from loguru import logger

import app.keyboards as kb
from app.cache.redis_logic import UserSession
from app.middleware import RateLimiter
from app.worker import push_all_users_to_db
banner_text = f'🎰 {html.bold("Magic Spin - Slot machine simulator")}\n\n💸 Win {html.bold("combinations:")}\n\n7️⃣7️⃣7️⃣ = Bid Amount x10\n⬜️⬜️⬜️ = Bid Amount x5\n🍋🍋🍋 = Bid Amount x2\n🍇🍇🍇 = Bid Amount x2\n\n{html.bold("This project is a non-commercial simulation of Telegram’s slot machine dice feature. It has been developed solely for educational and demonstration purposes.")}'

router = Router()
router.message.middleware(RateLimiter())
router.callback_query.middleware(RateLimiter())

logger.add("logs/log.log", rotation="1 day", level="INFO", enqueue=True)


class AuthorizationStatus(StatesGroup):
    unathorized = State()
    authorized = State()


async def get_coins(callback_from_handler: CallbackQuery) -> tuple:
    """
    Retrieve the bid amount and current coin balance for a user.

    Args:
        callback_from_handler (CallbackQuery): The callback query triggered by the user.

    Returns:
        tuple: (bid_amount, UserSession object, cached_coins)
    """
    amount = int(callback_from_handler.data.split(":")[1])
    session = UserSession(callback_from_handler.from_user.id)
    await session.ensure_session()
    cached_coins = int(await session.get_coins_qty())
    return amount, session, cached_coins


@router.message(CommandStart())
async def handle_cmd_start(message: Message, state: FSMContext) -> None:
    """
    Handle the /start command.

    - Checks user authorization status.
    - Sends a captcha for verification.
    - Displays welcome message and main menu upon success.

    Args:
        message (Message): Incoming message object.
        state (FSMContext): FSM context for the user state.
    """
    if await state.get_state() == AuthorizationStatus.authorized:
        await message.answer("Already logged in", reply_markup=kb.main_menu_keyboard)
    else:
        await state.set_state(AuthorizationStatus.unathorized)
        keyboard, correct_emoji = await kb.create_captcha_keyboard(message.from_user.id)
        await message.answer(f'Hello, {message.from_user.first_name},\nwelcome to Magic Spin Slot Machine Simulator!\n\nSolve a captcha to proceed\n\nClick on {correct_emoji} button below', reply_markup=keyboard)


@router.callback_query(F.data.startswith("captcha:"))
async def check_if_human(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Check the user's captcha response and authorize if correct.

    Args:
        callback (CallbackQuery): The callback query triggered by the captcha button.
        state (FSMContext): FSM context for the user state.
    """
    _, chosen_emoji, correct, user_id = callback.data.split(":")
    session = UserSession(user_id)
    await session.ensure_session()
    if chosen_emoji == correct:
        await state.set_state(AuthorizationStatus.authorized)
        await session.authorize_user()
        await session.get_coins_qty()
        await callback.answer(None)
        await callback.message.edit_text("You solved captcha! ✅")
        await callback.message.answer(banner_text, parse_mode="html", reply_markup=kb.main_menu_keyboard)
    else:
        await callback.answer("False!")
        await callback.message.edit_text("Try again! ⛔")


@router.callback_query(F.data == "main:spin")
async def get_bid_amount(callback: CallbackQuery) -> None:
    """
    Prompt the user to choose a bid amount for a spin.

    Args:
        callback (CallbackQuery): Callback query triggered by "Spin" button.
    """
    await callback.answer(None)
    await callback.message.edit_text("Choose the Bid Amount from below:", reply_markup=kb.bid_amounts_keyboard)


@router.callback_query(F.data == "main:earn")
async def add_coins_from_main(callback: CallbackQuery) -> None:
    """
    Prompt the user to choose an amount to add coins (top-up).

    Args:
        callback (CallbackQuery): Callback query triggered by "Get Coins" button.
    """
    await callback.answer(None)
    await callback.message.edit_text("Choose amount for a top up from below:", reply_markup=kb.add_coins_keyboard)


@router.callback_query(F.data.startswith("bid_amount:"))
async def send_slotmachine(callback: CallbackQuery) -> None:
    """
    Perform the slot machine spin based on user's bid.

    - Deducts coins for the bid.
    - Determines prize multiplier based on slot result.
    - Updates user coin balance accordingly.

    Args:
        callback (CallbackQuery): Callback query triggered by a bid amount button.
    """
    amount, session, cached_coins = await get_coins(callback)
    await callback.answer(None)
    if cached_coins > 0 and cached_coins >= amount:
        await callback.message.edit_text(f'You chose {amount} 🪙', reply_markup=None)
        result = await callback.message.answer_dice(emoji="🎰")
        prizes = {64: 10, 43: 2, 22: 2, 1: 5}
        multiplier = prizes.get(result.dice.value, 0)

        if multiplier:
            win = amount * multiplier
            new_balance = cached_coins + win
            await session.change_coins_qty(new_balance)
            await asyncio.sleep(2.2)
            await callback.message.answer(f'💰 {html.bold("JACKPOT")} 💰\n\n{html.bold("YOU GOT:")} {win} 🪙\n\nYour balance: {new_balance}', parse_mode="html", reply_markup=kb.main_menu_keyboard)
        else:
            new_balance = cached_coins - amount
            await session.change_coins_qty(new_balance)
            await asyncio.sleep(2.2)
            await callback.message.answer(f'😟 {html.bold("Not this time! Try again and WIN!")}\n\nYour balance: {new_balance}\n\nTap {html.bold("Get coins")} 🪙 if you need more!', parse_mode="html", reply_markup=kb.main_menu_keyboard)
    else:
        await callback.message.answer(f'😟 {html.bold("You ran out of coins!")} Add some: ', parse_mode="html", reply_markup=kb.add_coins_keyboard)


@router.callback_query(F.data.startswith("add_coins:"))
async def add_coins_from_spin(callback: CallbackQuery) -> None:
    """
    Top up user's balance.

    Args:
        callback (CallbackQuery): Callback query triggered by an "Add Coins" button.
    """
    amount, session, cached_coins = await get_coins(callback)
    await callback.answer(None)
    await session.change_coins_qty((cached_coins + amount))
    await callback.message.edit_text(f'Your balance is {cached_coins + amount} 🪙\n\nChoose an action from below:', reply_markup=kb.main_menu_keyboard)


@router.callback_query(F.data == "main:profile")
async def get_profile(callback: CallbackQuery) -> None:
    """
    Show the user's profile with name from Telegram and coin balance.

    Args:
        callback (CallbackQuery): Callback query triggered by "Profile" button.
    """
    session = UserSession(callback.from_user.id)
    await session.ensure_session()
    await callback.answer(None)
    await callback.message.edit_text(f'{html.bold("Your profile")} 👤\n\nName: {callback.from_user.full_name}\nCoins: {await session.get_coins_qty()} 🪙', parse_mode="html", reply_markup=kb.single_back_button)


@router.callback_query(F.data == "main:rules")
async def get_rules(callback: CallbackQuery) -> None:
    """
    Display bot rules.

    Args:
        callback (CallbackQuery): Callback query triggered by "Rules" button.
    """
    await callback.answer(None)
    await callback.message.edit_text(f'{html.bold("Rules")} 📖\n\n1. This project is for portfolio/demo purposes only\n2. This bot uses fake/demo coins — not real money\n3. Spamming or flooding will add you to the blacklist\n4. Removal from the blacklist is only possible via deletion from database. (In real-world project it would be done by admin)\n5. Commercial use or modifications for commercial use are allowed only with author’s permission and proper credit.\n\n{html.bold("Feel free to test/redact the bot!")}', parse_mode="html", reply_markup=kb.single_back_button)


@router.callback_query(F.data == "cancel")
async def go_to_main_from_bid_menu(callback: CallbackQuery):
    """
    Return the user to the main menu from bid or add coins menus.

    Args:
        callback (CallbackQuery): Callback query triggered by "Cancel" button.
    """
    await callback.answer(None)
    await callback.message.edit_text(banner_text, parse_mode="html", reply_markup=kb.main_menu_keyboard)

@router.error()
async def log_errors(event: ErrorEvent) -> None:
    """
    Cathces all errors from other handlers.

    Args:
        event (ErrorEvent): Internal event, should be used to receive errors while processing Updates from Telegram.
    """
    logger.error(f"Error caused by {event.exception}")
    logger.complete()

@router.shutdown()
async def save_redis_data():
    """
    Performs save of all data from cache to db on bot shutdown
    """
    logger.info("Saving cached data to database, please wait")
    await push_all_users_to_db(forced=True)
    logger.info("Cached data was successfully transfered to database. Shutting down...")

