import sqlite3

con = sqlite3.connect('db.sqlite')
cur = con.cursor()

query_users = '''
CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, username TEXT, first_name TEXT, last_name TEXT, platform TEXT, date_joined TEXT NOT NULL, last_interaction TEXT, status TEXT DEFAULT user, action TEXT DEFAULT меню);
'''

query_chats = '''
CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_chat INTEGER NOT NULL, vk_chat TEXT, status TEXT);
'''

query = '''
DELETE FROM chat;
'''


cur.executescript(query)
con.close()
