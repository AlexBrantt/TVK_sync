import telebot
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TG_TOKEN')

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def start_telegram_bot(send_to_vk_callback):
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        chat_id = message.chat.id
        # user_id = message.from_user.id
        # Отправляем сообщение в VK, вызывая переданную функцию
        if False:
            send_to_vk_callback(message.text)
        bot.send_message(chat_id, 'Вы еще не зареганы')

    # Запуск бота
    bot.polling()
