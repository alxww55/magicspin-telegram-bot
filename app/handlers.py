from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(CommandStart())
async def check_if_human(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.first_name}!")
    # TODO: add user id to database "unathorized"
    await message.answer(f"Solve a captcha to proceed\n\nClick on 🦆 button below")