from ..connect import session_maker
from ..models import User
from datetime import datetime
from loader import logger


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
        logger.info(f'Создан пользователь {user.id}, зовут {user.name}')
    return user

def user_exists(telegram_id):
    with session_maker() as session:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

def get_user(telegram_id):
    """ Вытаскиваем пользователя из БД"""
    with session_maker() as session:
        user: User = session.query(User).filter(User.telegram_id == telegram_id).first()
        return user

def get_user_by_id(user_id):
    """ Вытаскиваем пользователя из БД"""
    with session_maker() as session:
        return session.query(User).filter(User.id == user_id).first()

def get_users():
    with session_maker() as session:
        users: User = session.query(User).all()
        return users