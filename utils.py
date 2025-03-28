import datetime

from db_utils import user_create, user_exist


def register_user(message, platform, session=None):
    if platform == 'tg':
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
    elif platform == 'vk':
        user_id = message.object.message["from_id"]
        username = None
        user_info = session.users.get(
            user_ids=user_id, fields="first_name,last_name"
        )[0]
        first_name = user_info['first_name']
        last_name = user_info['last_name']
    else:
        print('Некорректный параметр платформы')
        return 'Некорректный параметр платформы'

    date_joined = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    last_interaction = date_joined
    user_data = (
        user_id,
        username,
        first_name,
        last_name,
        platform,
        date_joined,
        last_interaction,
    )
    if not user_exist(user_id):
        user_create(user_data)
        return 'Велком в бота'
    else:
        return 'Вы уже зареганы'
