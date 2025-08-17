from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb

router = Router()

@router.message(CommandStart())
async def handle_cmd_start(message: Message) -> None:
    keyboard, correct_emoji = await kb.create_captcha_keyboard(message.from_user.id)
    await message.answer(f"Hello, {message.from_user.first_name}!")
    # TODO: add user id to database "unathorized"
    await message.answer(f"Solve a captcha to proceed\n\nClick on {correct_emoji} button below", reply_markup=keyboard)

@router.callback_query(F.data.startswith("captcha:"))
async def check_if_human(callback: CallbackQuery) -> None:
    _, chosen_emoji, correct, user_id = callback.data.split(":")

    if chosen_emoji == correct:
        await callback.answer("Correct!")
        await callback.message.edit_text("You solved captcha! ✅")
        await callback.message.answer("Главное меню:", reply_markup=kb.main_menu_keyboard)
    else:
        await callback.answer("False!")
        await callback.message.edit_text("Try again! ⛔")