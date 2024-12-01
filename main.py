import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from db import get_user_id_by_username, get_all_chat_ids, insert_chat, update_employee_role  # Импортируем новые функции для изменения роли

# Устанавливаем логирование для отслеживания ошибок
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменная для хранения администратора
admin_id = None

# Функция старта
async def start(update: Update, context: CallbackContext):
    global admin_id
    user_id = update.message.from_user.id
    if admin_id is None:
        admin_id = user_id
        await update.message.reply_text("Вы стали администратором бота.")
    else:
        await update.message.reply_text(f"Администратор: {admin_id}")

# Функция помощи
async def help(update: Update, context: CallbackContext):
    help_text = (
        "Доступные команды:\n\n"
        "/start — Назначить администратором.\n"
        "/help — Показать список доступных команд.\n"
        "/set_role @username новая_должность — Назначить должность сотрудника.\n"
        "/delete @username — Удалить сотрудника из чатов.\n"
        "/register_chat — Зарегистрировать чат."
    )
    await update.message.reply_text(help_text)

# Функция для регистрации чата
async def register_chat(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    title = update.message.chat.title
    chat_type = update.message.chat.type

    # Добавляем chat_id в базу данных, если его там нет
    insert_chat(chat_id, title, chat_type)
    await update.message.reply_text(f"Чат {title} ({chat_id}) успешно зарегистрирован.")

# Функция для удаления пользователя
async def delete_user(update: Update, context: CallbackContext):
    global admin_id

    # Проверка, что команда вызвана администратором
    if update.message.from_user.id != admin_id:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Неверный формат команды. Используйте: /delete @username")
        return

    username = context.args[0].lstrip('@')  # Убираем символ @ из никнейма

    # Получаем user_id из базы данных
    user_id = get_user_id_by_username(username)
    if not user_id:
        await update.message.reply_text(f"Пользователь @{username} не найден.")
        return

    # Получаем все chat_id, в которых состоит бот
    chat_ids = get_all_chat_ids()

    if not chat_ids:
        await update.message.reply_text("Бот не состоит в ни одном чате для удаления пользователя.")
        return

    for chat_id in chat_ids:
        # Используем метод ban_chat_member для удаления пользователя
        try:
            await context.application.bot.ban_chat_member(chat_id, user_id)
            await update.message.reply_text(f"Пользователь @{username} забанен в чате {chat_id}.")
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя {username} в чате {chat_id}: {e}")
            await update.message.reply_text(f"Не удалось удалить @{username} в чате {chat_id}. Ошибка: {e}")

# Функция для назначения должности сотруднику
async def set_role(update: Update, context: CallbackContext):
    global admin_id

    # Проверка, что команда вызвана администратором
    if update.message.from_user.id != admin_id:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Неверный формат команды. Используйте: /set_role @username новая_должность")
        return

    username = context.args[0].lstrip('@')  # Убираем символ @ из никнейма
    new_role = context.args[1]  # Новая роль

    # Получаем user_id из базы данных
    user_id = get_user_id_by_username(username)
    if not user_id:
        await update.message.reply_text(f"Пользователь @{username} не найден.")
        return

    try:
        # Обновляем роль сотрудника в базе данных
        update_employee_role(user_id, new_role)
        await update.message.reply_text(f"Должность пользователя @{username} успешно обновлена на {new_role}.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении должности для пользователя {username}: {e}")
        await update.message.reply_text(f"Не удалось обновить должность пользователя @{username}. Ошибка: {e}")


# Основная функция для запуска основного бота
def main():
    # Указываем токен основного бота
    application = Application.builder().token("7978584231:AAFneaWEV_WG8JEipfCCdQuwAgImnAykVdw").build()

    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("delete", delete_user))  # Команда на удаление пользователя
    application.add_handler(CommandHandler("register_chat", register_chat))  # Команда на регистрацию чата
    application.add_handler(CommandHandler("set_role", set_role))  # Команда для назначения должности сотруднику
    application.add_handler(CommandHandler("help", help))  # Команда на вывод помощи

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
