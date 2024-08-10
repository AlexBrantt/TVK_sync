import sqlite3

# Если в текущей директории нет файла db.sqlite - 
# он будет создан; одновременно будет создано и соединение с базой данных.
# Если файл существует, метод connect просто подключится к базе.
con = sqlite3.connect('db.sqlite')

# Создаём специальный объект cursor для работы с БД.
# Вся дальнейшая работа будет вестись через методы этого объекта.
cur = con.cursor()

# Готовим SQL-запросы.
# Для читаемости запрос обрамлён в тройные кавычки и разбит построчно.

query_users= '''
CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, username TEXT, first_name TEXT, last_name TEXT, platform TEXT, date_joined TEXT NOT NULL, last_interaction TEXT, status TEXT DEFAULT user, status TEXT DEFAULT меню);
'''

query_chats= '''
CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, username TEXT, first_name TEXT, last_name TEXT, platform TEXT, date_joined TEXT NOT NULL, last_interaction TEXT, status TEXT DEFAULT user);
'''

query = '''
INSERT INTO settings (key, value) VALUES ('autocoupon_value', '20%');
'''
# Применяем запросы.
# cur.execute()
#con.commit()
# весь скрипт применить...
cur.executescript(query_users)
# Закрываем соединение с БД.
con.close()