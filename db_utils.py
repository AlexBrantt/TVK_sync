"""Модуль бд."""

import sqlite3

DB_NAME = 'db.sqlite'


def db_connect():
    """Подключение к БД."""
    return sqlite3.connect(DB_NAME)


def create_db():
    """Создание таблиц в БД."""
    queries = '''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        platform TEXT,
        date_joined TEXT NOT NULL,
        last_interaction TEXT,
        status TEXT DEFAULT 'user',
        action TEXT DEFAULT 'меню'
    );

    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_chat INTEGER NOT NULL,
        vk_chat INTEGER NOT NULL,
        status TEXT,
        sender INTEGER NOT NULL
    );
    '''
    with db_connect() as con:
        con.executescript(queries)


def check_and_create_db():
    """Проверяет наличие таблиц и создает их, если они отсутствуют."""
    with db_connect() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user';"
        )
        user_table_exists = cur.fetchone() is not None
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='chat';"
        )
        chat_table_exists = cur.fetchone() is not None

    if not user_table_exists or not chat_table_exists:
        print("Таблицы отсутствуют. Создаем...")
        create_db()
    else:
        print("Все таблицы на месте, продолжаем запуск.")


# ПОЛЬЗОВАТЕЛИ


def user_exist(user_id):
    """Проверяет есть ли запись о пользователе в бд."""
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT 1 FROM user WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    con.close()
    return result is not None


def user_create(data):
    """Добавляение пользователя в бд."""
    con = db_connect()
    try:
        cur = con.cursor()
        cur.execute(
            '''INSERT INTO user (user_id, username, first_name,
            last_name, platform, date_joined, last_interaction)
            VALUES (?, ?, ?, ?, ?, ?, ?);''',
            data,
        )
        con.commit()
        print("Данные пользователя успешно вставлены в базу данных.")
    except sqlite3.Error as e:
        print(f"Ошибка при вставке данных пользователя: {e}")
    finally:
        con.close()


def user_set_action(user_id, action):
    """Устанавлиет текущее действие пользователю."""
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "UPDATE user SET action = ? WHERE user_id = ?", (action, user_id)
    )
    con.commit()
    con.close()


# ЧАТЫ


def chat_ticket(data):
    """Отправить заявку на синхронизацию чатов."""
    con = db_connect()
    try:
        cur = con.cursor()

        # Проверка, существует ли запись с таким tg_chat и vk_chat
        cur.execute(
            '''SELECT COUNT(*) FROM chat 
            WHERE tg_chat = :tg_id AND vk_chat = :vk_id''',
            data,
        )
        if cur.fetchone()[0] > 0:
            return "Заявка на соединение уже была отправлена!"

        cur.execute(
            '''INSERT INTO chat (tg_chat, vk_chat, status, sender)
            VALUES (:tg_id, :vk_id, 'verify', :sender);''',
            data,
        )
        con.commit()
        print("Заявка на синхронизацию чатов добавлена в базу данных.")
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при отправке заявки чату: {e}")
        return f"Ошибка базы данных: {e}"
    finally:
        con.close()


def chat_status_get(data):
    con = db_connect()
    try:
        cur = con.cursor()
        cur.execute(
            '''SELECT status FROM chat WHERE tg_chat = ? AND vk_chat = ?''',
            data,
        )
        result = cur.fetchone()
        return (
            result[0] if result else None
        )  # Возвращаем только статус или None
    finally:
        con.close()


def chat_status_update(data):
    con = db_connect()
    try:
        cur = con.cursor()
        cur.execute(
            '''
            UPDATE chat 
            SET status = :new_status
            WHERE tg_chat = :tg_id 
            AND vk_chat = :vk_id;
            ''',
            data,
        )
        con.commit()
        if cur.rowcount == 0:
            print("⚠️ Ошибка: Не найдена запись для обновления!")
            return "⚠️ Ошибка: Заявка не найдена или уже обработана."
        print("✅ Статус успешно обновлен в БД!")
        return "✅ Статус успешно обновлен."
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return f"❌ Ошибка базы данных: {e}"
    finally:
        con.close()


def chat_status_delete(data):
    con = db_connect()
    try:
        cur = con.cursor()
        cur.execute(
            '''
            DELETE FROM chat 
            WHERE tg_chat = :tg_id AND vk_chat = :vk_id AND status = 'verify';
            ''',
            data,
        )
        con.commit()
        if cur.rowcount == 0:
            return "⚠️ Ошибка: Заявка уже обработана или не найдена!"
        return "❌ Заявка на синхронизацию отклонена!"
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return f"❌ Ошибка базы данных: {e}"
    finally:
        con.close()


def get_chat_redirect(platform, sender_id):
    con = db_connect()
    cur = con.cursor()
    if platform == 'tg':
        cur.execute(
            "SELECT vk_chat, status FROM chat WHERE tg_chat = ?", (sender_id,)
        )
    elif platform == 'vk':
        cur.execute(
            "SELECT tg_chat, status FROM chat WHERE vk_chat = ?", (sender_id,)
        )
    else:
        return False
    result = cur.fetchone()
    con.close()
    print(result)
    return result


# Ну тут крч обдумать над
def chat_confirm(platform, sender_id):
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "UPDATE chat SET status = ? WHERE user_id = ?", ('confirmed', user_id)
    )
    con.commit()
    con.close()
