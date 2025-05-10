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

async def apply_pixel(input_path, filename):
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

async def apply_cartoon(file_path, filename, line_size=11, blur_value=7, k=9):
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

async def apply_pencil(input_path, filename):
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

async def apply_sepia(input_path, filename):
    img = cv2.imread(input_path)

    # Создаем матрицу сепия-фильтра
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])

    # Применяем фильтр
    sepia_img = cv2.transform(img, sepia_filter)

    # Ограничиваем значения пикселей, чтобы не выходили за пределы 0-255
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, sepia_img)
    return output_path

async def apply_black_white(input_path, filename):
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, gray)
    return output_path

async def apply_hdr(input_path, filename):
    img = cv2.imread(input_path)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)

    merged = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    # Повышение резкости
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, sharpened)
    return output_path

async def apply_blur_background(input_path, filename):
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    mask = cv2.GaussianBlur(mask, (21, 21), 0)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0

    blurred = cv2.GaussianBlur(img, (35, 35), 0)
    result = img * mask + blurred * (1 - mask)

    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, result.astype(np.uint8))
    return output_path

async def apply_vintage(input_path, filename):
    img = cv2.imread(input_path)

    # Наложение сепии
    sepia = np.array([[0.272, 0.534, 0.131],
                      [0.349, 0.686, 0.168],
                      [0.393, 0.769, 0.189]])
    vintage = cv2.transform(img, sepia)
    vintage = np.clip(vintage, 0, 255)

    # Виньетирование
    rows, cols = vintage.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols/2)
    kernel_y = cv2.getGaussianKernel(rows, rows/2)
    kernel = kernel_y * kernel_x.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    vignette = np.copy(vintage)
    for i in range(3):
        vignette[:,:,i] = vignette[:,:,i] * mask


    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, vignette.astype(np.uint8))
    return output_path

async def apply_oil_painting(input_path, filename):
    img = cv2.imread(input_path)
    oil = cv2.xphoto.oilPainting(img, 7, 1)  # (size, dynRatio)
    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, oil)
    return output_path

async def apply_color_splash_red(input_path, filename):
    img = cv2.imread(input_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Маска для красного цвета (два диапазона)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    result = np.where(red_mask[:, :, np.newaxis] == 255, img, gray_bgr)

    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, result)
    return output_path

async def apply_glitch(input_path, filename):
    img = cv2.imread(input_path)
    rows, cols, _ = img.shape

    glitch = img.copy()

    # Смещение каналов
    glitch[:, :, 0] = np.roll(glitch[:, :, 0], 5, axis=1)
    glitch[:, :, 1] = np.roll(glitch[:, :, 1], -5, axis=1)

    # Добавление "шумовых" линий
    for i in range(0, rows, 10):
        if i % 20 == 0:
            glitch[i:i+2, :, :] = 255 - glitch[i:i+2, :, :]

    # Добавление гауссовского шума
    noise = np.random.normal(0, 15, img.shape).astype(np.uint8)
    glitch = cv2.add(glitch, noise)


    # Определяем путь для сохранения файла
    output_dir = "outfotos"  # Папка для выходных файлов
    output_path = os.path.join(output_dir, filename)  # Формируем путь сохранения
    cv2.imwrite(output_path, glitch)
    return output_path

