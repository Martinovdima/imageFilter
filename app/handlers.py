from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types
from bd import create_or_get_user, add_image_processing_request, update_processed_image
import app.keyboard as kb
import os
import traceback
from aiogram.utils.chat_action import ChatActionSender
from functions import convert_to_pixel_openCV, convert_to_cartoon_openCV, convert_to_pencil_openCV


router = Router()

class ImageProcessing(StatesGroup):
    waiting_for_image = State()
@router.message(CommandStart())
async def cmd_start(message: Message):
    await create_or_get_user(message.from_user.id, message.from_user.username)
    photo = FSInputFile("image/collage.webp")
    text = "🔹 Этот бот может изменить твое изображение 🔹\n\n📸 Выбирай формат... 📸"
    await message.answer_photo(photo=photo, caption=text, reply_markup=await kb.art_keyboard())

@router.message(Command('help'))
async def help(message: Message):
    photo = FSInputFile('image/help.jpg')
    text = (
        "🎨  Этот бот может изменить твое изображение  🎨\n"
        "📸  Выбирай формат с помощью кнопок  📸\n"
        "📂  Загружай изображение  📂\n"
        "💾  Скачивай результат  💾\n"
        "📌  Я принимаю JPG, JPEG, WEBP, BMP или PNG  📌"
    )
    await message.answer_photo(photo=photo, caption=text, parse_mode="MarkdownV2")

@router.callback_query(F.data.startswith("art_"))
async def process_art_callback(callback: types.CallbackQuery, state: FSMContext):
    selected_art = callback.data.split("_")[1]  # Получаем название фильтра
    await state.update_data(selected_art=selected_art)  # Сохраняем выбор фильтра
    await callback.message.answer("Отправьте изображение, которое хотите обработать 📷")

    await state.set_state(ImageProcessing.waiting_for_image)  # Переключаем FSM в ожидание фото

    current_state = await state.get_state()  # Проверяем состояние
    print(f"📌 Установлено состояние: {current_state}")

    await callback.answer()  # Закрываем callback (убираем "часики")


@router.message(ImageProcessing.waiting_for_image, F.photo | F.document)
async def process_image(message: types.Message, state: FSMContext):
    try:
        print(f'📸 Поймал изображение')

        from main import bot  # Локальный импорт, чтобы избежать циклических импортов

        async with ChatActionSender.upload_photo(bot, message.chat.id):
            user_data = await state.get_data()
            selected_art = user_data.get("selected_art")

            if selected_art not in ['PIXEL', 'CARTOON', 'PENCIL']:
                text = "❗ Сначала нужно выбрать формат\n\n📸 Выбирай... 📸"
                await message.answer(text=text, reply_markup=await kb.art_keyboard())
                return

            print(f'🎨 Выбранный фильтр: {selected_art}')

            user_id = message.from_user.id

            # Проверяем, что отправлено: фото или документ
            if message.photo:
                file_id = message.photo[-1].file_id
                file_info = await bot.get_file(file_id)
                file_path = file_info.file_path
                file_name = os.path.basename(file_path)
            elif message.document:
                file_id = message.document.file_id
                file_info = await bot.get_file(file_id)
                file_path = file_info.file_path
                file_name = message.document.file_name

                # Проверяем расширение файла
                allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
                file_ext = os.path.splitext(file_name)[-1].lower()

                if file_ext not in allowed_extensions:
                    await message.answer("❌ Неверный формат! Отправь изображение в формате JPG, JPEG, WEBP, BMP или PNG.")
                    return

            request_id = await add_image_processing_request(user_id, file_id, selected_art)
            print(f'Изображение сохранено в базе данных')

            # Скачиваем файл
            save_path = os.path.join("infotos", file_name)
            await bot.download_file(file_path, save_path)
            print(f'💾 Файл сохранен в: {save_path}')

            await message.answer(f"Вы выбрали фильтр: {selected_art}\nИзображение загружено! 🔄 Обрабатываем...")

            # Применяем фильтр
            if selected_art == 'PIXEL':
                processed_photo_path = await convert_to_pixel_openCV(save_path, file_name)
            elif selected_art == 'CARTOON':
                processed_photo_path = await convert_to_cartoon_openCV(save_path, file_name)
            elif selected_art == 'PENCIL':
                processed_photo_path = await convert_to_pencil_openCV(save_path, file_name)
            else:
                await message.answer(f"❌ Такого формата нет!")
                return

            print(f'✅ Обработанное изображение: {processed_photo_path}')

            # Отправляем обработанное изображение
            output_path = FSInputFile(processed_photo_path)
            text = "🔶 Твое изображение готово! 🔶\n\n📸 Выбирай следующий формат... 📸"
            sent_message = await message.answer_photo(photo=output_path, caption=text,
                                                      reply_markup=await kb.art_keyboard())

            if sent_message.photo:
                sent_file_id = sent_message.photo[-1].file_id
                await update_processed_image(request_id, sent_file_id)
            else:
                print('⚠️ Ошибка: sent_message.photo = None')

            os.remove(save_path)
            os.remove(processed_photo_path)

            await state.clear()  # Очищаем состояние пользователя
            print('🧹 Состояние пользователя очищено')

    except Exception as e:
        print(f'⚠ Ошибка: {e}')
        print(traceback.format_exc())  # Выводит полную трассировку ошибки
        await message.answer("❌ Произошла ошибка при обработке изображения.")


@router.message(F.photo | F.document)
async def send_foto(message: types.Message):
    text = "❗ Сначала нужно выбрать формат \n\n📸 Выбирай... 📸"
    await message.answer(text=text, reply_markup=await kb.art_keyboard())

@router.message(~F.photo)
async def handle_non_photo_messages(message: types.Message):
    await message.answer("Я принимаю только фото! 📷")