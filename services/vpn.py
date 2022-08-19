from db.queries import get_all_servers, get_all_user_ips, get_server, get_server_users, update_item
from subnet import IPv4Network
from .keys import generate_key, public_key
import subprocess
from datetime import datetime
from db.models import User, Server


def choose_server():
    """ Выбираем сервер для пользователя, где число пользователей меньше 10 """
    servers = get_all_servers()
    for server in servers:
        if server.users_cnt < 10:
            return server

def choose_ip(server):
    """ Генерируем IP, чтобы не совпадал с уже имеющимися"""
    user_ips = get_all_user_ips(server.id)
    lan = IPv4Network(server.lan)
    user_ip = str(lan.random_ip())
    while user_ip in user_ips or user_ip == server.lan_ip:
        user_ip = lan.random_ip()
    return user_ip

def generate_user_config(user: User, server: Server):
    """ Генерируется конфиг для пользователя """
    user_ip = choose_ip(server)
    priv_key = generate_key()
    pub_key = public_key(priv_key)
    user.ip = user_ip
    user.public_key = pub_key
    user.server = server
    user.status = 'executed'
    user.vpn_created_at = datetime.now()
    server.users_cnt += 1
    with open(f'servers/instance/{server.name}_peer.txt', 'r') as peer:
        peer_config = peer.read()
        with open(f'users/config/{user.id}.conf', 'w') as cfg:
            cfg.write(
                '[Interface]\n'
                f'PrivateKey = {priv_key}\n'
                f'Address = {user.ip}/32\n'
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

def generate_server_config_by_id(server_id):
    """
         Генерирует конфиг для сервера. Конфиг генерируется каждый раз с нуля, пробегая
         по всем пользователям данного сервера, чтобы в него не попали пользователи
         с просроченым VPN.
    """
    server = get_server(server_id)
    server_users = get_server_users(server_id)
    date = datetime.now().strftime('%d%m%Y')
    with open(f'servers/instance/{server.name}_wg0.txt', 'r') as srv:
        interface = srv.read()
        with open(f"servers/config/{server.name}_{date}.conf", 'w') as cfg:
            cfg.write(f'{interface}\n')
            for user in server_users:
                if user.status != 'expired':
                    cfg.write(
                        f'#user_{user.id}\n'
                        '[Peer]\n'
                        f'PublicKey = {user.public_key}\n'
                        f'AllowedIPs = {user.ip}\n'
                    )
                else:
                    print(f'У пользователя с id={user.id} не оплачен VPN')
    subprocess.run(f'scp servers/config/{server.name}_{date}.conf root@{server.wan_ip}:/etc/wireguard/wg0.conf', shell=True)
    subprocess.run(f'systemctl -H root@{server.wan_ip} restart wg-quick@wg0.service', shell=True)
    return True

def create_vpn(user, server):
    server_id = server.id
    user_cfg = generate_user_config(user, server)
    server_cfg = generate_server_config_by_id(server_id)
    if user_cfg and server_cfg:
        return True
    else:
        return False


#     subprocess.run(f'scp /home/crash/projects/hercules_net_bot/servers_config/{server.name}_{date}.conf root@{server.wan_ip}:/etc/wireguard/wg0.conf',  shell=True)
#     subprocess.run(f'systemctl -H root@{server.wan_ip} restart wg-quick@wg0.service',  shell=True)
