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

main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Magic Spin 🎰", callback_data="main:spin")],
    [InlineKeyboardButton(text="Profile 👤", callback_data="main:profile"), InlineKeyboardButton(text="Earn coins 🪙", callback_data="main:earn")],
    [InlineKeyboardButton(text="Support 🛠️", callback_data="main:support"), InlineKeyboardButton(text="Rules 📖", callback_data="main:rules")]])

bid_amounts_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="10 🪙", callback_data="bid_amount:10"), InlineKeyboardButton(text="20 🪙", callback_data="bid_amount:20")],
    [InlineKeyboardButton(text="50 🪙", callback_data="bid_amount:50"), InlineKeyboardButton(text="100 🪙", callback_data="bid_amount:100")],
    [InlineKeyboardButton(text="Cancel ❌", callback_data="cancel")]])
