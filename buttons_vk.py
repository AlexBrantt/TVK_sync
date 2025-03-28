import json

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import vk_module


def send_verification_request_vk(tg_chat, vk_chat, username):
    """Отправить заявку на синхронизацию в ВК"""
    vk_msg = f'''🔹 **Платформа:** Telegram  
🔹 **Отправитель:** @{username}  

Выберите действие:'''

    keyboard = VkKeyboard(inline=True)
    keyboard.add_callback_button(
        label="✅ Принять заявку",
        color=VkKeyboardColor.POSITIVE,
        payload=json.dumps(
            {"command": "accept", "tg_chat": tg_chat, "vk_chat": vk_chat}
        ),
    )
    keyboard.add_callback_button(
        label="❌ Отклонить заявку",
        color=VkKeyboardColor.NEGATIVE,
        payload=json.dumps(
            {"command": "decline", "tg_chat": tg_chat, "vk_chat": vk_chat}
        ),
    )

    vk_module.vk.messages.send(
        peer_id=vk_chat,
        message=vk_msg,
        random_id=0,
        keyboard=keyboard.get_keyboard(),
    )
