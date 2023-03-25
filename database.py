import psycopg2
from config import host, user, password, database

# подключение к базе данных
conn = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
conn.autocommit = True


# создание таблицы пользователей
def create_table_users():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id serial,
                first_name varchar(50) NOT NULL,
                last_name varchar(50) NOT NULL,
                vk_id varchar(15) NOT NULL PRIMARY KEY,
                vk_link text);"""
        )
    return True


# создание таблицы просмотренных пользователей
def create_table_seen_users():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(15) PRIMARY KEY);"""
        )
    return True


# заполнение таблицы пользователей
def insert_data_users(first_name, last_name, vk_id, vk_link):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (first_name, last_name, vk_id, vk_link) VALUES (%s, %s, %s, %s)",
            (first_name, last_name, vk_id, vk_link)
        )


# заполнение таблицы просмотренные пользователи
def insert_data_seen_users(vk_id):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO seen_users (vk_id) VALUES (%s)",
            (vk_id,)
        )


# выбор непросмотренных пользователей
def select(offset):
    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT u.first_name, u.last_name, u.vk_id, u.vk_link, su.vk_id FROM users AS u
                LEFT JOIN seen_users AS su ON u.vk_id = su.vk_id
                WHERE su.vk_id IS NULL
                OFFSET {offset};"""
        )
        return cur.fetchone()


# удаление таблицы пользователей
def drop_users():
    with conn.cursor() as cur:
        cur.execute(
            """DROP TABLE IF EXISTS users;"""
        )


# удаление таблицы просмотренных пользователей
def drop_seen_users():
    with conn.cursor() as cur:
        cur.execute(
            """DROP TABLE  IF EXISTS seen_users;"""
        )


# вызов всех функций
def creating_database():
    drop_users()
    drop_seen_users()
    create_table_users()
    create_table_seen_users()
