import asyncio
from aiogram import F, Router, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.cache.redis_logic as redis
import app.database.requests as rq

router = Router()


class AuthorizationStatus(StatesGroup):
    unathorized = State()
    authorized = State()


async def send_slotmachine(callback: CallbackQuery) -> None:
    amount = int(callback.data.split(":")[1])
    result = await callback.message.answer_dice(emoji="🎰")
    match(result.dice.value):
        case 64:
            await asyncio.sleep(2.2)
            await callback.answer(None)
            await callback.message.answer(f"💰 {html.bold("JACKPOT")} 💰\n\n{html.bold(f"YOU GOT: {amount * 10}")} 🪙", parse_mode="html", reply_markup=kb.main_menu_keyboard)
        case 43:
            await asyncio.sleep(2.2)
            await callback.answer(None)
            await callback.message.answer(f"💰 {html.bold("WIN")} 💰\n\n{html.bold(f"YOU GOT: {amount * 2}")} 🪙", parse_mode="html", reply_markup=kb.main_menu_keyboard)
        case 22:
            await asyncio.sleep(2.2)
            await callback.answer(None)
            await callback.message.answer(f"💰 {html.bold("WIN")} 💰\n\n{html.bold(f"YOU GOT: {amount * 2}")} 🪙", parse_mode="html", reply_markup=kb.main_menu_keyboard)
        case 1:
            await asyncio.sleep(2.2)
            await callback.answer(None)
            await callback.message.answer(f"💰 {html.bold("WIN")} 💰\n\n{html.bold(f"YOU GOT: {amount * 5}")} 🪙", parse_mode="html", reply_markup=kb.main_menu_keyboard)
        case _:
            await asyncio.sleep(2.2)
            await callback.answer(None)
            await callback.message.answer(f"😟 {html.bold("Not this time! Try again and WIN!")}\n\nYour ballance: amount\n\nTap Earn if you runned out of coins", parse_mode="html", reply_markup=kb.main_menu_keyboard)


@router.message(CommandStart())
async def handle_cmd_start(message: Message, state: FSMContext) -> None:
    # TODO: Check if user in Blacklist (redis)
    black_list = []
    if message.from_user.id in black_list:
        return
    elif await state.get_state() == AuthorizationStatus.authorized:
        await message.answer("Already logged in", reply_markup=kb.main_menu_keyboard)
    else:
        await redis.calculate_login_attempts(message.from_user.id)
        user_attempts = await redis.get_cached_attempts(message.from_user.id)
        if int(user_attempts) >= 5:
            # TODO: Add user to Blacklist
            # ONLY FOR DEBUG!!!
            await redis.clear_login_attempts(message.from_user.id)
            await message.answer("[+] DEBUG added to blacklist\n\n[+] DEBUG reseted login attempts")
        await state.set_state(AuthorizationStatus.unathorized)
        await rq.register_unauthorized_users(message.from_user.id)
        keyboard, correct_emoji = await kb.create_captcha_keyboard(message.from_user.id)
        await message.answer(f"Hello, {message.from_user.first_name},\nwelcome to Magic Spin Slot Machine Simulator!\n\n[+] DEBUG login_attempts: {user_attempts}\nSolve a captcha to proceed\n\nClick on {correct_emoji} button below", reply_markup=keyboard)


@router.callback_query(F.data.startswith("captcha:"))
async def check_if_human(callback: CallbackQuery, state: FSMContext) -> None:
    _, chosen_emoji, correct, user_id = callback.data.split(":")

    if chosen_emoji == correct:
        await state.set_state(AuthorizationStatus.authorized)
        await redis.clear_login_attempts(user_id)
        await rq.add_user_to_authorized(int(user_id))
        await callback.answer(None)
        await callback.message.edit_text("You solved captcha! ✅")
        await callback.message.answer(f"🎰 {html.bold("Magic Spin - Slot machine simulator")}\n\n💸 You can win following {html.bold("prizes:")}\n\n7️⃣7️⃣7️⃣ = Bid Amount x10\n\n⬜️⬜️⬜️ = Bid Amount x5\n\n🍋🍋🍋 = Bid Amount x2\n\n🍇🍇🍇 = Bid Amount x2\n\n{html.bold("This is just a simulator")}", parse_mode="html", reply_markup=kb.main_menu_keyboard)
    else:
        await callback.answer("False!")
        await callback.message.edit_text("Try again! ⛔")


@router.callback_query(F.data == "main:spin")
async def get_bid_amount(callback: CallbackQuery) -> None:
    await callback.answer(None)
    await callback.message.edit_text("Choose the Bid Amount from below:", reply_markup=kb.bid_amounts_keyboard)


@router.callback_query(F.data == "bid_amount:10")
async def handle_10(message: Message):
    await send_slotmachine(message)


@router.callback_query(F.data == "bid_amount:20")
async def handle_20(message: Message):
    await send_slotmachine(message)


@router.callback_query(F.data == "bid_amount:50")
async def handle_50(message: Message):
    await send_slotmachine(message)


@router.callback_query(F.data == "bid_amount:100")
async def handle_100(message: Message):
    await send_slotmachine(message)


@router.callback_query(F.data == "Cancel ❌")
async def go_to_main_from_bid_menu(callback: CallbackQuery):
    await callback.message.edit_text(f"🎰 {html.bold("Magic Spin - Slot machine simulator")}\n\n💸 You can win following {html.bold("prizes:")}\n\n7️⃣7️⃣7️⃣ = Bid Amount x10\n\n⬜️⬜️⬜️ = Bid Amount x5\n\n🍋🍋🍋 = Bid Amount x2\n\n🍇🍇🍇 = Bid Amount x2\n\nThis is just a simulator\n\n🎰 {html.bold("Spin now and WIN!")}", parse_mode="html", reply_markup=kb.main_menu_keyboard)
