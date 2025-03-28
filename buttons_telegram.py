from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

import telegram_module


def send_verification_request(tg_chat, vk_chat, first_name, last_name):
    """Отправить заявку с кнопками подтверждения и отклонения"""
    tg_msg = f'''Вашему чату пришла заявка на синхронизацию!
🔹 Платформа: ВКонтакте  
🔹 Отправитель: {first_name} {last_name}  

Выберите действие:'''

    keyboard = InlineKeyboardMarkup()
    button_accept = InlineKeyboardButton(
        text="✅ Принять заявку", callback_data=f"accept:{tg_chat}:{vk_chat}"
    )
    button_decline = InlineKeyboardButton(
        text="❌ Отклонить заявку",
        callback_data=f"decline:{tg_chat}:{vk_chat}",
    )
    keyboard.add(button_accept, button_decline)  # Добавляем обе кнопки

    telegram_module.bot.send_message(tg_chat, tg_msg, reply_markup=keyboard)
