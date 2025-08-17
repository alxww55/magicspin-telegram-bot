from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.captcha import emojis_list, choose_control_emoji, generate_captcha_items


async def create_captcha_keyboard(user_id: int) -> tuple:
    keyboard = InlineKeyboardBuilder()
    correct_emoji = choose_control_emoji(emojis_list)
    captcha_items = generate_captcha_items(correct_emoji)

    for emoji in captcha_items:
        keyboard.add(InlineKeyboardButton(
            text=emoji, callback_data=f"captcha:{emoji}:{correct_emoji}:{user_id}"))

    return keyboard.adjust(2).as_markup(), correct_emoji

main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Play 🎰")],
    [KeyboardButton(text="Profile 👤"), KeyboardButton(text="Support 🛠️")]],
    input_field_placeholder="Choose an action below:",
    one_time_keyboard=True,
    resize_keyboard=True)
