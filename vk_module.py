import json
import os

import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from db_utils import (
    chat_status_delete,
    chat_status_get,
    chat_status_update,
    chat_ticket,
    get_chat_redirect,
)
from utils import register_user

load_dotenv()

VK_TOKEN = os.getenv('VK_TOKEN')
VK_GROUP_ID = os.getenv("VK_GROUP_ID")

vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)


def send_message(peer_id, message):
    vk.messages.send(peer_id=peer_id, message=message, random_id=0)


def handle_vk_callback(event):
    if event.type != VkBotEventType.MESSAGE_EVENT:
        print("Некорректный тип события, пропускаем")
        return

    payload = event.object.payload
    command = payload.get("command")
    tg_chat = payload.get("tg_chat")
    vk_chat = payload.get("vk_chat")

    try:
        current_status = chat_status_get((tg_chat, vk_chat))
        if current_status == "confirmed" or current_status == None:
            # Если чат уже подтверждён, скрываем анимацию
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(
                    {
                        "type": "show_snackbar",
                        "text": "⚠️ Заявка уже обработана.",
                    }
                ),
            )
            return
        if command == "accept":
            # Подтверждаем заявку
            data = {
                'tg_id': tg_chat,
                'vk_id': vk_chat,
                'new_status': 'confirmed',
            }
            chat_status_update(data)

            # Уведомляем пользователя
            vk.messages.send(
                peer_id=event.object.peer_id,
                message="✅ Заявка принята!",
                random_id=0,
            )

            # Завершаем анимацию с сообщением
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(
                    {
                        "type": "show_snackbar",
                        "text": "✅ Заявка принята!",
                    }
                ),
            )

        elif command == "decline":
            data = {'tg_id': tg_chat, 'vk_id': vk_chat}
            result = chat_status_delete(data)

            # Уведомление об удалении
            vk.messages.send(
                peer_id=event.object.peer_id, message=result, random_id=0
            )

            # Завершаем анимацию с сообщением
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(
                    {
                        "type": "show_snackbar",
                        "text": "❌ Заявка отклонена",
                    }
                ),
            )

    except Exception as e:
        print(f"Ошибка при обработке кнопки: {e}")


def listen_to_vk(send_to_telegram_callback, send_verification_request):
    print("VK Starting longpoll listener...")

    for event in longpoll.listen():
        print(f"VK Received event: {event}")

        # Обработка сообщений
        if event.type == VkBotEventType.MESSAGE_NEW:
            print("VK Message event received")
            message = event.object.message["text"].lower().strip()
            peer_id = event.object.message["peer_id"]

            # Обработка команды /start
            if message.startswith('/start'):
                response = register_user(event, platform='vk', session=vk)
                send_message(peer_id, response)

            # Обработка команды /connect
            elif message.startswith('/connect'):
                args = message.split()[1:]

                if not args or not args[0].isdigit():
                    msg = f'''Для подключения к чату используйте: /connect (id чата)

Команда для подключению к вашему чату: /connect {peer_id}'''
                    send_message(peer_id, msg)
                else:

                    data = {
                        'tg_id': args[0],
                        'vk_id': peer_id,
                        'sender': peer_id,
                    }
                    ticket_result = chat_ticket(data)
                    if ticket_result is True:
                        user_info = vk.users.get(
                            user_ids=event.object.message["from_id"],
                            fields="first_name,last_name",
                        )[0]
                        first_name = user_info['first_name']
                        last_name = user_info['last_name']
                        send_verification_request(
                            args[0], peer_id, first_name, last_name
                        )
                        send_message(
                            peer_id, 'В указанный чат отправлен запрос'
                        )
                    else:
                        send_message(peer_id, ticket_result)

            # Обработка других сообщений

            else:
                chat_redirect = get_chat_redirect('vk', peer_id)
                if chat_redirect is None:
                    msg = f'''Чат не связан! Для подключения к чату используйте: /connect id чата
        id вшаего чата: {peer_id}'''
                    send_message(peer_id, msg)
                    return
                chat_tg_id, chat_status = chat_redirect[0], chat_redirect[1]
                if chat_status == 'confirmed':
                    sender_info = vk.users.get(
                        user_ids=event.object.message["from_id"],
                        fields="first_name,last_name",
                    )[0]
                    send_to_telegram_callback(chat_tg_id, event, sender_info)

        elif event.type == VkBotEventType.MESSAGE_EVENT:
            print("Button click event received")
            handle_vk_callback(event)
