from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

ARTS = ['PIXEL', 'CARTOON', 'PENCIL']

async def art_keyboard():
    keyboard = InlineKeyboardBuilder()
    for art in ARTS:
        keyboard.add(InlineKeyboardButton(text=art, callback_data=f'art_{art}'))
    return keyboard.as_markup()