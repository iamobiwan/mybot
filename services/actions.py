from db.models import User
from db.queries import get_vpns, get_user_by_id, update_item, get_all_servers, get_server_vpns, get_pending_vpns, get_server
from datetime import datetime
from loader import bot
import subprocess
from keyboards.reply import start_executed_user
from loader import logger


@logger.catch
async def check_vpn_expire():
    logger.info('Запускаем проверку на истечение срока подписки...')
    vpns = get_vpns()
    date = datetime.now()
    if vpns:
        for vpn in vpns:
            if vpn.status == 'trial' or vpn.status == 'paid':
                if date > vpn.expires_at:
                    user = get_user_by_id(vpn.user_id)
                    logger.info(f'У пользователя {user.id} {user.name} истек срок действия VPN (был {vpn.status})')
                    vpn.status = 'expired'
                    update_item(vpn)
                    await bot.send_message(user.telegram_id, 'Срок действия VPN истек. Продлите подписку.')
    else:
        logger.info('Все подписки актульны')

async def update_server_config(server):
    vpns = get_server_vpns(server.id)
    date = datetime.now().strftime('%d%m%Y')
    with open(f'servers/instance/{server.name}_wg0.txt', 'r') as file:
        text = file.read()
        for vpn in vpns:
            if vpn.status != 'expired':
                text += f'\n#user_{vpn.user_id}\n'\
                        f'[Peer]\n'\
                        f'PublicKey = {vpn.public_key}\n'\
                        f'AllowedIPs = {vpn.ip}\n'
        with open(f"servers/config/{server.name}_{date}.conf", 'w') as config:
            config.write(text)
    subprocess.run(f'scp servers/config/{server.name}_{date}.conf root@{server.wan_ip}:/etc/wireguard/wg0.conf', shell=True)
    subprocess.run(f'systemctl -H root@{server.wan_ip} restart wg-quick@wg0.service', shell=True)
    logger.info(f'Обновлена конфигурация для сервера {server.name}, ip: {server.wan_ip}')

@logger.catch
async def rebuild_server_config():
    logger.info('Запускаем ежедневное обновление конфигурации на серверах...')
    servers = get_all_servers()
    for server in servers:
        await update_server_config(server)
    logger.info('Обновление конфигурации на серверах завершено')

async def rebuild_server_config_by_id(server_ids):
    logger.info('Обновление конфигурации на серверах для ожидающих пользователей')
    for server_id in server_ids:
        server = get_server(server_id)
        await update_server_config(server)
    logger.info('Обновление конфигурации на серверах завершено')

@logger.catch
async def check_pending_vpns():
    logger.info('Проверяем очередь новых VPN...')
    data = get_pending_vpns()
    server_ids = []
    if data:
        logger.info('Есть ожидающие VPN...')
        for value in data.values():
            vpn = value.get('vpn')
            user = value.get('user')
            if vpn.server_id not in server_ids:
                server_ids.append(vpn.server_id)
            vpn.status = 'trial'
            with open(f'users/qr/{user.id}.png', 'rb') as photo:
                await bot.send_message(user.telegram_id, 'Вот ваш QR код.\nНажмите "Инструкция" для получения подробных указаний по установке')
                await bot.send_photo(user.telegram_id, photo, reply_markup=start_executed_user)
            update_item(vpn)
        await rebuild_server_config_by_id(server_ids)
                

    