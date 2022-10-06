#!/usr/bin/python3


from datetime import datetime
from loader import logger, config
import subprocess
from db.models import Server
from db.queries import get_all_servers


servers = get_all_servers()
date = datetime.now().strftime('%d%m%Y')

def backup_config(server: Server, date):
    backup = subprocess.run(['cp', f'servers/{server.name}/wg0.conf', f'servers/backup/{server.name}_{date}.conf'])
    if backup.stderr:
        logger.warning(backup.stderr)
    else:
        logger.info(f'Создан backup для сервера {server.name}.')
        
def send_config():
    for server in servers:
        backup_config(server, date)
        logger.info(f'Заливаем конфиг на сервер {server.name}...')
        subprocess.run(f'(sudo wg-quick strip servers/{server.name}/wg0.conf)>'\
                    f'servers/{server.name}/sync.conf', shell=True)
        send = subprocess.run(
            ['rsync', '-avz', '--timeout=10',
            f'servers/{server.name}/',
            f'root@{server.wan_ip}:/etc/wireguard/'],
            capture_output=True,
            text=True)
        if send.stdout:
            logger.info(send.stdout)
            logger.info(f'На сервер {server.name} залита новая конфигурация')
        elif send.stderr:
            logger.warning(send.stderr)
            logger.warning(f'Конфигурация не ушла на сервер {server.name}!')

send_config()
