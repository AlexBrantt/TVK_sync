from threading import Thread

import telegram_module
import vk_module
from buttons_telegram import send_verification_request
from buttons_vk import send_verification_request_vk
from db_utils import check_and_create_db


def send_message_to_vk(chat_id, message):
    '''Функция отправляющая сообщение в вк'''
    message = f'[{message.from_user.username}]\n\n{message.text}'
    vk_module.send_message(chat_id, message)


def send_message_to_telegram(chat_id, event, sender_info):
    '''Функция отправляющая сообщение в тг'''
    first_name = sender_info['first_name']
    last_name = sender_info['last_name']
    text = event.object.message["text"]
    message = f'*{first_name} {last_name}*\n\n{text}'
    telegram_module.bot.send_message(
        chat_id=chat_id, text=message, parse_mode='MarkdownV2'
    )


if __name__ == '__main__':
    check_and_create_db()

    vk_thread = Thread(
        target=vk_module.listen_to_vk,
        args=(send_message_to_telegram, send_verification_request),
    )
    telegram_thread = Thread(
        target=telegram_module.start_telegram_bot,
        args=(send_message_to_vk, send_verification_request_vk),
    )

    # Запуск потоков
    vk_thread.start()
    telegram_thread.start()

    # Ожидание завершения потоков
    vk_thread.join()
    telegram_thread.join()
