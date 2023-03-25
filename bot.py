from keyboard import sender
from main import *

offset = 0  # сдвиг
line = range(0, 1000)  # поочередный перебор найденных людей

for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = event.user_id
        sender(user_id, request)
        if request == 'начать поиск':
            creating_database()
            bot.find_user(user_id)
            bot.write_msg(event.user_id, f'Привет, нашёл пару, нажми на кнопку "Вперёд"')
            bot.find_persons(user_id, offset)
        elif request == 'вперёд':
            for person in line:
                offset += 1
                bot.find_persons(user_id, offset)
                break
        else:
            bot.write_msg(event.user_id, 'Нажмите ниже на кнопку <Начать поиск> или <Вперед>')
