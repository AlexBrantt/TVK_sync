import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
import os

load_dotenv()

VK_TOKEN = os.getenv('VK_TOKEN')

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def listen_to_vk(send_to_telegram_callback):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            message = event.text
            send_to_telegram_callback(message)
