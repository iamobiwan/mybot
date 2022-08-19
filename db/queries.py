from .connect import session_maker
from .models import User, Server
from datetime import datetime

def create_user(telegram_id, name):
    """ Создаем пользователя в БД """
    user = User(
        telegram_id=telegram_id,
        name=name,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        )
    with session_maker() as session:
        session.add(user)
        session.commit()

def get_user(telegram_id):
    """ Вытаскиваем пользователя из БД"""
    with session_maker() as session:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

def update_item(item):
    with session_maker() as session:
        session.add(item)
        session.commit()

def get_server(server_id):
    """ Получить конкретный сервер """
    with session_maker() as session:
        return session.query(Server).get(server_id)  

def get_server_users(server_id):
    """ Получить всех пользователей на сервере """
    with session_maker() as session:
        return session.query(User).filter(User.server_id == server_id).all()

def get_all_servers():
    """ Получить все сервера """
    with session_maker() as session:
        return session.query(Server).all()

def get_all_user_ips(server_id):
    """ Возвращает все ip пользователей с определенного сервера"""
    with session_maker() as session:
        return [item.ip for item in session.query(User.ip).filter(User.server_id == server_id)]