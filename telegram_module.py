import logging
import os

import telebot
from dotenv import load_dotenv

from db_utils import (
    chat_status_delete,
    chat_status_update,
    chat_ticket,
    get_chat_redirect,
)
from utils import register_user

logging.basicConfig(level=logging.INFO)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TG_TOKEN')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

try:

    def start_telegram_bot(send_to_vk_callback, send_verification_request_vk):

        @bot.message_handler(commands=['start'])
        def user_register(message):
            """Добавляение пользователя в бд."""
            bot.send_message(
                message.chat.id, register_user(message, platform='tg')
            )

        @bot.message_handler(commands=['connect'])
        def command_connect(message):
            """Подключение чата."""
            args = message.text.split()[1:]
            chat_id = message.chat.id
            username = message.from_user.username
            if not args or not args[0].isdigit():
                msg = f'''Для подключения к чату используйте: /connect (id чата)

Команда для подключению к вашему чату: /connect {chat_id}'''
                bot.reply_to(message, msg)
                return

            vk_id = args[0]

            data = {'tg_id': chat_id, 'vk_id': vk_id, 'sender': chat_id}
            ticket_result = chat_ticket(data)

            if ticket_result is True:
                send_verification_request_vk(chat_id, vk_id, username)
                bot.send_message(chat_id, 'В указанный чат отправлен запрос')
            else:
                bot.send_message(chat_id, ticket_result)

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith("accept:")
        )
        def accept_callback(call):
            _, tg_id, vk_id = call.data.split(":")
            data = {'tg_id': tg_id, 'vk_id': vk_id, 'new_status': 'confirmed'}

            chat_status_update(data)
            bot.send_message(tg_id, "✅ Заявка на синхронизацию принята!")

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith("decline:")
        )
        def decline_callback(call):
            _, tg_id, vk_id = call.data.split(":")
            data = {'tg_id': int(tg_id), 'vk_id': int(vk_id)}

            result = chat_status_delete(data)
            bot.send_message(call.message.chat.id, result)

        @bot.message_handler(func=lambda message: True)
        def handle_message(message):
            chat_id = message.chat.id
            chat_redirect = get_chat_redirect('tg', chat_id)
            if chat_redirect is None:
                msg = f'''Чат не связан! Для подключения к чату используйте: /connect id чата
    id вшаего чата: {chat_id}'''
                bot.send_message(chat_id, msg)
                return
            chat_vk_id, chat_status = chat_redirect[0], chat_redirect[1]
            if chat_status == 'confirmed':
                send_to_vk_callback(chat_vk_id, message)
                msg = get_chat_redirect('tg', chat_id)
                bot.send_message(
                    chat_id, f'адресс получателя: {chat_redirect}'
                )
            else:
                bot.send_message(
                    chat_id, 'Чат еще не подтвердил синхронизацию'
                )

        # Запуск бота
        bot.polling()

except Exception as e:
    logging.error(f"Ошибка в Telegram боте: {e}")
