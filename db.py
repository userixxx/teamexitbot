import sqlite3

# Функция для подключения к базе данных
def get_db_connection():
    try:
        conn = sqlite3.connect('employees.db')  # Файл базы данных
        conn.row_factory = sqlite3.Row  # Для получения результатов в виде словарей
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Функция для получения user_id по username
def get_user_id_by_username(username):
    conn = get_db_connection()
    user_id = None
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user:
                user_id = user['user_id']
        except sqlite3.Error as e:
            print(f"Ошибка при запросе user_id: {e}")
        finally:
            conn.close()
    return user_id

# Функция для получения всех chat_id
def get_all_chat_ids():
    conn = get_db_connection()
    chat_ids = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT chat_id FROM chats')
            chat_ids = [row['chat_id'] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Ошибка при запросе chat_id: {e}")
        finally:
            conn.close()
    return chat_ids

# Функция для добавления chat_id в таблицу чатов
def insert_chat(chat_id, title, chat_type):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO chats (chat_id, title, chat_type) VALUES (?, ?, ?)',
                           (chat_id, title, chat_type))
            conn.commit()
            print(f"Чат {title} ({chat_id}) успешно добавлен.")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении чата в базу данных: {e}")
        finally:
            conn.close()

# Функция для добавления пользователя в таблицу users
def insert_user(user_id, username, role, start_date):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Проверка на существование пользователя
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            existing_user = cursor.fetchone()
            if existing_user:
                return  # Пользователь уже есть в базе, ничего не делаем

            cursor.execute('INSERT INTO users (user_id, username, role, start_date) VALUES (?, ?, ?, ?)',
                           (user_id, username, role, start_date))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении пользователя: {e}")
        finally:
            conn.close()

# Функция для получения всех сотрудников
def get_all_employees():
    conn = get_db_connection()
    employees = []
    if conn:
        try:
            cursor = conn.cursor()
            # Извлекаем всех сотрудников, сортируем по username
            cursor.execute('''
                SELECT user_id, username, role, start_date
                FROM users
                ORDER BY username
            ''')
            employees = cursor.fetchall()  # Получаем все результаты
        except sqlite3.Error as e:
            print(f"Ошибка при запросе сотрудников: {e}")
        finally:
            conn.close()
    return employees

# Функция для обновления роли сотрудника
def update_employee_role(user_id, new_role):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET role = ? WHERE user_id = ?', (new_role, user_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении роли: {e}")
        finally:
            conn.close()

# Создание таблицы users и chats, если их нет
def create_table():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Создаем таблицу пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    role TEXT NOT NULL,
                    start_date TEXT NOT NULL
                )
            ''')
            # Создаем таблицу чатов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    chat_type TEXT NOT NULL
                )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            conn.close()
