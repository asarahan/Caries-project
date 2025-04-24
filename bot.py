import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

# Загрузка модели
model = tf.keras.models.load_model("best_model.keras")

# Описание диагнозов и рекомендаций
diagnosis_dict = {
    "Healthy": "Зуб здоров. Регулярная гигиена и осмотр раз в 6 месяцев.",
    "Superficial": "Поверхностный кариес. Лечение у терапевта, пломба.",
    "Medium": "Средний кариес. Требуется расширение полости и постановка пломбы.",
    "Deep": "Глубокий кариес.Возможно переходящий в пульпит. Вероятно, потребуется эндодонтическое лечение (лечение каналов)."
}

# Предобработка изображения
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))  # размер зависит от твоей модели
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = "received.jpg"
    await photo_file.download_to_drive(photo_path)

    img_array = preprocess_image(photo_path)
    prediction = model.predict(img_array)
    class_index = np.argmax(prediction[0])
    class_names = ["Healthy", "Superficial", "Medium", "Deep"]
    diagnosis = class_names[class_index]
    advice = diagnosis_dict[diagnosis]

    response = f"Диагноз: {diagnosis}\nРекомендации: {advice}"
    await update.message.reply_text(response)

# /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне рентгеновский снимок зуба, и я скажу диагноз.")

# Запуск
def main():
    token = os.getenv("TELEGRAM_TOKEN")  # установи переменную окружения на PythonAnywhere

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен!")
    app.run_polling()

if _name_ == "_main_":
    main()
