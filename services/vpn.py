from db.queries import get_all_servers, get_all_user_ips, update_item, create_trial_vpn
from subnet import IPv4Network
from .keys import generate_key, public_key
import subprocess
from datetime import datetime
from db.models import User, Server, Vpn
from loader import logger


def choose_server():
    """ Выбираем сервер для пользователя, где число пользователей меньше 10 """
    servers = get_all_servers()
    for server in servers:
        if server.users_cnt < 10:
            return server

def choose_ip(server: Server):
    """ Генерируем IP, чтобы не совпадал с уже имеющимися"""
    user_ips = get_all_user_ips(server.id)
    lan = IPv4Network(server.lan)
    user_ip = str(lan.random_ip())
    while user_ip in user_ips or user_ip == server.lan_ip:
        user_ip = str(lan.random_ip())
    return user_ip

def generate_user_config(user: User, server: Server):
    """ Генерируется конфиг для пользователя """
    user_ip = choose_ip(server)
    priv_key = generate_key()
    pub_key = public_key(priv_key)
    create_trial_vpn(user.id, server.id, user_ip, pub_key)
    user.status = 'pending'
    user.updated_at = datetime.now()
    server.users_cnt += 1
    with open(f'servers/instance/{server.name}_peer.txt', 'r') as peer:
        peer_config = peer.read()
        with open(f'users/config/{user.id}.conf', 'w') as cfg:
            cfg.write(
                '[Interface]\n'
                f'PrivateKey = {priv_key}\n'
                f'Address = {user_ip}/32\n'
                'DNS = 8.8.8.8\n\n'
                f'{peer_config}'
            )
    subprocess.run(
        f'qrencode -t png -o users/qr/{user.id}.png < users/config/{user.id}.conf',
        shell=True
        )
    update_item(user)
    update_item(server)
    return True

def create_vpn(user, server):
    user_cfg = generate_user_config(user, server)
    if user_cfg:
        return True
    else:
        return False
