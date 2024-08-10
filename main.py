from threading import Thread
import vk_module
import telegram_module
from dotenv import load_dotenv
import os

load_dotenv()

VK_USER_ID = os.getenv('AlEX_VK')
TELEGRAM_CHAT_ID = os.getenv('AlEX_TG')


def send_message_to_vk(message):
    vk_module.vk.messages.send(
        user_id=VK_USER_ID,
        random_id=0,
        message=message
    )


def send_message_to_telegram(message):
    telegram_module.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message
    )


if __name__ == '__main__':
    vk_thread = Thread(target=vk_module.listen_to_vk,
                       args=(send_message_to_telegram,))
    telegram_thread = Thread(target=telegram_module.start_telegram_bot,
                             args=(send_message_to_vk,))

    # Запуск потоков
    vk_thread.start()
    telegram_thread.start()

    # Ожидание завершения потоков
    vk_thread.join()
    telegram_thread.join()
