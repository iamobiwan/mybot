from .connect import session_maker
from .models import User, Server, Vpn, Tariff, Bill
from datetime import datetime, timedelta
from loader import logger
import const

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

def user_exists(telegram_id):
    with session_maker() as session:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

def get_user_data(telegram_id):
    """ Вытаскиваем пользователя из БД"""
    with session_maker() as session:
        user: User = session.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            try:
                vpn: Vpn = user.vpn[0]
            except:
                vpn = None
            return {
                'user': user,
                'vpn': vpn
            }

def get_user_by_id(user_id):
    """ Вытаскиваем пользователя из БД"""
    with session_maker() as session:
        return session.query(User).filter(User.id == user_id).first()

def get_pending_vpns():
    with session_maker() as session:
        pending_vpns = session.query(Vpn).filter(Vpn.status == 'pending').all()
        data = []
        for vpn in pending_vpns:
            data.append({
                'vpn': vpn,
                'user': vpn.user
            })
        return data

def get_vpns():
    """ Получить все vpn """
    with session_maker() as session:
        return session.query(Vpn).all()

def get_server_vpns(server_id):
    """ Получить всех пользователей на сервере """
    with session_maker() as session:
        return session.query(Vpn).filter(Vpn.server_id == server_id).all()

def update_item(item):
    with session_maker() as session:
        session.add(item)
        session.commit()

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

def create_trial_vpn(user_id, server_id, user_ip, pub_key):
    user_vpn = Vpn(
        user_id=user_id,
        server_id=server_id,
        ip=user_ip,
        public_key=pub_key,
        status='pending',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=datetime.now() + timedelta(minutes=const.TRIAL_TTL)
    )
    with session_maker() as session:
        session.add(user_vpn)
        session.commit()

def get_all_tariffs():
    with session_maker() as session:
        return session.query(Tariff).all()

def get_tariff(tariff_id):
    with session_maker() as session:
        return session.query(Tariff).filter(Tariff.id == tariff_id).first()

def create_bill(vpn, tariff):
    label = f'{vpn.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    pay_url = f'https://yoomoney.ru/quickpay/confirm.xml?receiver=4100117941854976'\
              f'&quickpay-form=shop&sum={tariff.price}&label={label}'
    bill = Bill(
        status='pending',
        vpn_id=vpn.id,
        tariff_id=tariff.id,
        pay_url=pay_url,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=datetime.now() + timedelta(minutes=const.TRIAL_TTL)
    )
    with session_maker() as session:
        session.add(bill)
        session.commit()
        return bill.id

def get_bill(bill_id):
    with session_maker() as session:
        return session.query(Bill).filter(Bill.id == bill_id).first()

def get_pending_bills_data_by_vpn(vpn_id):
    with session_maker() as session:
        bills = session.query(Bill).filter(
            Bill.vpn_id == vpn_id,
            Bill.status == 'pending'
            ).all()
        data = []
        for bill in bills:
            data.append({
                    'bill': bill,
                    'tariff': bill.tariff
                })
        return data