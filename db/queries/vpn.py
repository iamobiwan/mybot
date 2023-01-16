from ..connect import session_maker
from ..models import Server, Vpn, User
from datetime import datetime, timedelta
from loader import logger
import const


def create_vpn(user, server, user_ip, pub_key):
    user_vpn = Vpn(
        user_id=user.id,
        server_id=server.id,
        ip=user_ip,
        public_key=pub_key,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    with session_maker() as session:
        session.add(user_vpn)
        session.commit()

def get_pending_users():
    with session_maker() as session:
        pending_users = session.query(User).filter(User.vpn_status == 'pending').all()
        return pending_users

def get_vpns():
    """ Получить все vpn """
    with session_maker() as session:
        return session.query(Vpn).all()

def get_server_vpns(server_id):
    """ Получить всех пользователей на сервере """
    with session_maker() as session:
        return session.query(Vpn).filter(Vpn.server_id == server_id).all()

def get_server(server_id):
    """ Получить конкретный сервер """
    with session_maker() as session:
        return session.query(Server).get(server_id)  

def get_all_servers():
    """ Получить все сервера """
    with session_maker() as session:
        return session.query(Server).all()

def get_all_user_ips(server_id):
    """ Возвращает все ip пользователей с определенного сервера"""
    with session_maker() as session:
        return [item.ip for item in session.query(Vpn.ip).filter(Vpn.server_id == server_id)]
