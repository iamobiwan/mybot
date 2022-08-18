from .connect import session_maker
from .models import User
from datetime import datetime

def create_user(telegram_id, name):
    """ Создаем пользователя в БД """
    user = User(telegram_id=telegram_id, name=name, created_at=datetime.now())
    with session_maker() as session:
        session.add(user)
        session.commit()