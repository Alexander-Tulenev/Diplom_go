import vk_api
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from database import *
from config import user_token, comm_token
from vk_api.exceptions import ApiError


class VKBot:
    def __init__(self):
        print('Бот запущен')
        self.vk = vk_api.VkApi(token=comm_token)  # авторизация для сообщества
        self.longpoll = VkLongPoll(self.vk)  # метод для работы с сообщениями

    def write_msg(self, user_id, message):
        """Метод для отправки сообщений"""
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    def get_sex(self, user_id):
        """Получение пола пользователя (моего) и изменение его на противоположный"""
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'user_ids': user_id,
                  'fields': 'sex',
                  'v': '5.131'}
        try:
            response = requests.get(url, params=params).json()
            info_list = response['response']
            for gender in info_list:
                if gender.get('sex') == 2:
                    return 1
                elif gender.get('sex') == 1:
                    return 2
        except ApiError:
            self.write_msg(user_id, 'Ошибка получения токена user_token')

    def get_age_low(self, user_id):
        """Получение нижней границы возраста для поиска"""
        self.write_msg(user_id, 'Введите нижний порог возраста: ')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                try:
                    age = int(event.text)
                    if 16 <= age <= 60:
                        return age
                    else:
                        self.write_msg(user_id, 'Возраст должен быть от 16 до 60 лет')
                except ValueError:
                    self.write_msg(user_id, 'Введите возраст цифрами')

    def get_age_high(self, user_id):
        """Получение верхней границы возраста для поиска"""
        self.write_msg(user_id, 'Введите верхний порог возраста: ')
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                try:
                    age = int(event.text)
                    if 17 <= age <= 60:
                        return age
                    else:
                        self.write_msg(user_id, 'Возраст должен быть от 17 до 60 лет')
                except ValueError:
                    self.write_msg(user_id, 'Введите возраст цифрами')

    def get_city_id(self, user_id, city_name):
        """Получение id города пользователя (моего) по наименованию"""
        url = 'https://api.vk.com/method/database.getCities'
        params = {
            'access_token': user_token,
            'country_id': 1,
            'q': city_name,
            'v': '5.131',
            'lang': 'ru',
        }
        try:
            response = requests.get(url, params=params).json()
            for city in response['response']['items']:
                if city['title'].lower() == city_name.lower():
                    return city['id']
        except (KeyError, StopIteration):
            self.write_msg(user_id, f'Не удалось найти город "{city_name}"')

    def find_city(self, user_id):
        """Получение информации о городе пользователя (моего)"""
        url = f'https://api.vk.com/method/users.get'
        params = {'access_token': user_token,
                  'fields': 'city',
                  'user_ids': user_id,
                  'v': '5.131'}
        try:
            response = requests.get(url, params=params).json()
            info_dict = response['response']
            for object_city in info_dict:
                if 'city' in object_city:
                    city = object_city.get('city')
                    city_id = str(city.get('id'))
                    return city_id
                elif 'city' not in object_city:
                    self.write_msg(user_id, 'Введите название вашего города: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.get_city_id(user_id, city_name)
                            if id_city != '' or id_city is not None:
                                return str(id_city)
                            else:
                                break
        except KeyError:
            self.write_msg(user_id, 'Что-то пошло не так...')

    def find_user(self, user_id):
        """Поиск подходящего пользователя"""
        url = f'https://api.vk.com/method/users.search'
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_sex(user_id),
                  'age_from': self.get_age_low(user_id),
                  'age_to': self.get_age_high(user_id),
                  'city': self.find_city(user_id),
                  'fields': 'is_closed, id, first_name, last_name',
                  'status': 1,
                  'count': 1000}
        try:
            response = requests.get(url, params=params).json()
            print(response)  # отладочная информация
            dict_user = response['response']['items']
            print(dict_user)
            for person_dict in dict_user:
                if not person_dict.get('is_closed'):
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'vk.com/id' + str(person_dict.get('id'))
                    insert_data_users(first_name, last_name, vk_id, vk_link)
                else:
                    continue
            return f'Поиск завершён'
        except ApiError:
            self.write_msg(user_id, 'Ошибка в методе поиска пользователя')

    def get_photos_id(self, user_id):
        """Получение ID фото с ранжированием"""
        url = 'https://api.vk.com/method/photos.getAll'
        params = {'access_token': user_token,
                  'owner_id': user_id,
                  'extended': 1,
                  'count': 25,
                  'v': '5.131'}
        try:
            response = requests.get(url, params=params).json()
            dict_photos = dict()
            list_photos = response['response']['items']
            for photo in list_photos:
                photo_id = str(photo.get('id'))
                i_likes = photo.get('likes')
                if i_likes.get('count'):
                    likes = i_likes.get('count')
                    dict_photos[likes] = photo_id
            list_of_ids = sorted(dict_photos.items(), reverse=True)
            print(list_of_ids)  # [(8009, '457239019')] такой результат выводит
            return list_of_ids
        except KeyError:
            self.write_msg(user_id, 'id фотографии получить не удалось')

    def get_photo_n(self, user_id, n):
        """Получение id n-й фотографии"""
        list_photo_id = self.get_photos_id(user_id)
        count = 0
        for photo_id in list_photo_id:
            count += 1
            if count == n:
                return photo_id[1]

    def send_photo(self, user_id, message, offset, photo_number):
        """Отправка n-й фотографии"""
        photo_id = self.get_photo_n(person_id(offset), photo_number)
        self.vk.method('messages.send', {'user_id': user_id,
                                         'access_token': user_token,
                                         'message': message,
                                         'attachment': f'photo{person_id(offset)}_{photo_id}',
                                         'random_id': 0})

    def find_persons(self, user_id, offset):
        self.write_msg(user_id, found_person_info(offset))
        insert_data_seen_users(person_id(offset))
        self.get_photos_id(person_id(offset))
        for i in range(1, 4):
            photo = self.get_photo_n(person_id(offset), i)
            if photo is not None:
                self.vk.method('messages.send', {'user_id': user_id,
                                                 'access_token': user_token,
                                                 'message': f'Фото номер {i}',
                                                 'attachment': f'photo{person_id(offset)}_{photo}',
                                                 'random_id': 0})
            else:
                self.write_msg(user_id,
                               f'проблема с получением фотографий удовлетворяющих поиску по лайкам, или их нет')
                break


bot = VKBot()


def found_person_info(offset):
    """Вывод информации о найденном пользователе"""
    tuple_person = select(offset)
    list_person = []
    for info in tuple_person:
        list_person.append(info)
    return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}'


def person_id(offset):
    """Вывод id найденного пользователя"""
    tuple_person = select(offset)
    list_person = []
    for info in tuple_person:
        list_person.append(info)
    return str(list_person[2])
