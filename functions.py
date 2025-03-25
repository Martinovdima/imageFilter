import cv2
import os
import numpy as np
from aiogram import Bot
from aiogram.types import BotCommand

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь")
    ]
    await bot.set_my_commands(commands)

async def convert_to_pixel_openCV(input_path, filename):
    # Загружаем изображение
    input = cv2.imread(input_path)

    # Получаем размер изображения
    height, width = input.shape[:2]

    # Желаемый "пикселизированный" размер
    w, h = (128, 128)

    # Уменьшаем размер изображения
    temp = cv2.resize(input, (w, h), interpolation=cv2.INTER_LINEAR)

    # Увеличиваем обратно
    output = cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)

    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов

    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, output)  # Сохраняем изображение

    return output_path  # Возвращаем путь к обработанному изображению

async def convert_to_cartoon_openCV(file_path, filename, line_size=11, blur_value=7, k=9):
    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, blur_value)
    edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
    data = np.float32(img).reshape((-1, 3))

    # Задаем критерии
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)

    # Внедряем метод k-средних
    ret, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    result = center[label.flatten()]
    result = result.reshape(img.shape)
    blurred = cv2.bilateralFilter(result, d=9, sigmaColor=250, sigmaSpace=250)
    cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)

    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов

    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения

    cv2.imwrite(output_path, cartoon)

    return output_path

async def convert_to_pencil_openCV(input_path, filename):
    img = cv2.imread(input_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    invert = cv2.bitwise_not(gray_img)
    blur = cv2.GaussianBlur(invert, (21, 21), 0)
    invert_blur = cv2.bitwise_not(blur)
    sketch = cv2.divide(gray_img, invert_blur, scale=256.0)
    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, sketch)
    return output_path