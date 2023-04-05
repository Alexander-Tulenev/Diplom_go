from keyboard import sender
from main import *
import time

offset = 0 # сдвиг
current_user = 0 # индекс текущего юзера в памяти

users: List[dict] = list()
users_seen: List[dict] = list()

creating_database()

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = event.user_id
        sender(user_id, request)

        if request == 'начать поиск':
            users = bot.find_users(user_id)
            if len(users):
                bot.write_msg(user_id, f'Привет, нашёл {len(users)} пар, нажимай кнопку "Вперёд"')
                offset += len(users)

            else:
                bot.write_msg(user_id, f'Никого к сожалению не нашёл! Попробуй другие параметры для поиска!')

        elif request == 'вперёд':

            if users_seen != users:
                user_data = users[current_user]
                print(user_data)
                current_user += 1

                users_seen.append(user_data)

                bot.write_msg(user_id, f'{user_data.get("first_name")} {user_data.get("last_name")}, ссылка - {user_data.get("user_link")}')

                user_images = bot.get_photos_id(user_data.get('id'))

                for counter, photo_data in enumerate(user_images):
                    bot.send_photo(
                        user_id=user_id,
                        person_id=user_data.get('id'),
                        photo_id=photo_data[-1],
                        counter=counter + 1
                    )

            else:
                users_seen, current_user = list(), 0

                users = bot.find_users(user_id, offset)

        else:
            bot.write_msg(user_id, 'Нажмите ниже на кнопку <Начать поиск> или <Вперед>')

        # Check if there has been any activity for the last 5 seconds
        time_since_last_request = time.time() - event.timestamp
        if time_since_last_request > 300:
            bot.write_msg(user_id, 'До скорых встреч. я спать')
