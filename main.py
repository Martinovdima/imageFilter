import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv
from bd import init_db
from functions import set_bot_commands
from app.handlers import router


load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(storage=MemoryStorage())

os.makedirs("infotos", exist_ok=True)
os.makedirs("outfotos", exist_ok=True)

async def main():
    dp.include_router(router)
    await set_bot_commands(bot)
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
