from paramiko import SSHClient, AutoAddPolicy
import os
from loader import bot, logger, config


@logger.catch
async def sync_config(server):
    logger.info(f'Начинаю синхронизацию конфигурации сервера {server.name}...')
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()
    try:
        client.connect(server.wan_ip, username='obiwan')
        sftp = client.open_sftp()
        sftp.put(f'servers/{server.name}/wg0.conf', '/etc/wireguard/wg0.conf')
        logger.info('Файл скопирован')
        if sftp.stat('/etc/wireguard/wg0.conf').st_size == os.stat(f'servers/{server.name}/wg0.conf').st_size:
            logger.info('Успешно синхронизировано')
        else:
            logger.warning('Не синхронизировано') 
    except TimeoutError:
        logger.warning('Не удается подключиться к серверу, синхронизация не выполнена')


@logger.catch
async def check_config(server):
    logger.info('Начинаю проверку конфигурации...')
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()
    try:
        client.connect(server.wan_ip, username='obiwan')
        sftp = client.open_sftp()
        remote_file = sftp.open('/etc/wireguard/wg0.conf').read()
        with open(f'servers/{server.name}/wg0.conf', 'rb') as f:
            local_file = f.read()
            if local_file == remote_file:
                logger.info('Файлы идентичны')
            else:
                logger.warning('Файлы не совпадают!')
                for admin in config.tg_bot.admin_ids:
                    await bot.send_message(admin, f'Конфигурация не залилась на сервер {server.name}, ip: {server.wan_ip}')
                    logger.warning(f'Конфигурация сервера {server.name}, ip: {server.wan_ip} не обновилась!')
    except TimeoutError:
        logger.warning('Не удается подключиться к серверу, проверка не выполнена')

