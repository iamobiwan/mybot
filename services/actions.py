from db.models import User
from db.queries import get_vpns, get_user_by_id, update_item, get_all_servers, get_server_vpns, get_pending_users
from datetime import datetime
from loader import bot
import subprocess
from keyboards.reply import start_executed_user


async def check_vpn_expire():
    vpns = get_vpns()
    date = datetime.now()
    for vpn in vpns:
        if vpn.status == 'trial' or vpn.status == 'paid':
            if date > vpn.expires_at:
                user = get_user_by_id(vpn.user_id)
                vpn.status = 'expired'
                update_item(vpn)
                await bot.send_message(user.telegram_id, 'Срок действия VPN истек. Продлите подписку.')
    print('Проверка на expire')

async def rebuild_server_config():
    servers = get_all_servers()
    date = datetime.now().strftime('%d%m%Y')
    for server in servers:
        vpns = get_server_vpns(server.id)
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
    print('Ребилд из ребилд')

async def check_pending_users():
    pending_users = get_pending_users()
    if pending_users:
        for user in pending_users:
            user.status = 'executed'
            with open(f'users/qr/{user.id}.png', 'rb') as photo:
                await bot.send_message(user.telegram_id, 'Вот ваш QR код.\nНажмите "Инструкция" для получения подробных указаний по установке')
                await bot.send_photo(user.telegram_id, photo, reply_markup=start_executed_user)
            update_item(user)
        await rebuild_server_config()
        print('Ребилд из пендинг')
    
                

    