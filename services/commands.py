import subprocess
from db.models import Server
from loader import logger


async def send_config(server: Server, date):
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

async def check_config(server: Server, date):
    logger.info(f'Начинаем проверку конфигурации сервера {server.name}...')        
    remote_sync_config = subprocess.run(
        ['ssh', '-o ConnectTimeout=1', '-o ConnectionAttempts=1',
        f'root@{server.wan_ip}',
        'cat /etc/wireguard/sync.conf'],
        capture_output=True, text=True)
    remote_wg0_config = subprocess.run(
        ['ssh', '-o ConnectTimeout=1', '-o ConnectionAttempts=1',
        f'root@{server.wan_ip}',
        'cat /etc/wireguard/wg0.conf'],
        capture_output=True, text=True)
    with open(f'servers/{server.name}/sync.conf', 'r') as file:
        local_sync_config = file.read()
    with open(f'servers/backup/{server.name}_{date}.conf', 'r') as file:
        local_wg0_config = file.read()
    if remote_sync_config.stdout == local_sync_config and remote_wg0_config.stdout == local_wg0_config:
        return True
    else:
        return False

async def backup_config(server: Server, date):
    backup = subprocess.run(['cp', f'servers/{server.name}/wg0.conf', f'servers/backup/{server.name}_{date}.conf'])
    if backup.stderr:
        logger.warning(backup.stderr)
    else:
        logger.info(f'Создан backup для сервера {server.name}.')
    