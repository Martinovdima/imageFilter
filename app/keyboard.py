from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

ARTS = ['PIXEL', 'CARTOON', 'PENCIL', 'SEPIA', 'BLK&WHT', 'HDR', 'BLUR', 'VINTAGE', 'OIL', 'SPLASH', 'GLITCH']

async def art_keyboard():
    keyboard = InlineKeyboardBuilder()
    for art in ARTS:
        keyboard.add(InlineKeyboardButton(text=art, callback_data=f'art_{art}'))
    keyboard.adjust(3)
    return keyboard.as_markup()