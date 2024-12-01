import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from db import insert_user, create_table, get_all_employees  # Импортируем функцию для получения всех сотрудников

# Создание таблицы, если она не существует
create_table()

# Устанавливаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)  # Уровень DEBUG для отладки
logger = logging.getLogger(__name__)

# Функция старта для сотрудника
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Если username пустое, заменим его на 'Не указан'
    if not username:
        username = "Не указан"

    # Роль и дата начала
    role = 'Сотрудник'  # С заглавной буквы
    start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Логируем данные для отладки
    logger.debug(f"Авторизация пользователя: {username}, {user_id}, роль: {role}, дата начала: {start_date}")

    # Добавляем информацию о пользователе в базу данных
    try:
        # Проверка, существует ли уже такой пользователь в базе
        insert_user(user_id, username, role, start_date)

        # Форматированное сообщение с выводом информации
        message = (
            f"Добро пожаловать в ICM WOMAN.\n"
            f"Вы успешно авторизованы, @{username}.\n"
            f"Ваш ID: {user_id}.\n"
            f"Роль: {role}.\n"
            f"Начало работы: {start_date}"
        )
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя в базу данных: {e}")
        await update.message.reply_text(f"Произошла ошибка при добавлении пользователя в базу данных. Пожалуйста, попробуйте позже.")

# Функция помощи
async def help(update: Update, context: CallbackContext):
    help_text = (
        "Доступные команды:\n\n"
        "/start — Начать взаимодействие с ботом.\n"
        "/help — Показать список доступных команд.\n"
        "/search — Показать список сотрудников."
    )
    await update.message.reply_text(help_text)

# Функция для поиска сотрудников по имени
async def search(update: Update, context: CallbackContext):
    # Получаем всех сотрудников из базы данных
    employees = get_all_employees()

    if employees:
        result_text = "Список сотрудников:\n\n"
        for employee in employees:
            result_text += f"Username: @{employee['username']}, Должность: {employee['role']}\n"
    else:
        result_text = "Не найдено сотрудников."

    await update.message.reply_text(result_text)

# Основная функция для запуска второго бота
def main():
    # Указываем токен второго бота для сотрудников
    application = Application.builder().token("7238226805:AAGmBc-GCMZAUqKV2sbrqESg5wN5gmJ3QLk").build()

    # Регистрация команд
    application.add_handler(CommandHandler("start", start))  # Команда для старта
    application.add_handler(CommandHandler("help", help))  # Команда для получения помощи
    application.add_handler(CommandHandler("search", search))  # Команда для получения списка сотрудников

    # Запуск второго бота
    application.run_polling()

if __name__ == '__main__':
    main()
