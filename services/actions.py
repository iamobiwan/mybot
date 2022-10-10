from db.models import Server, User
from db.queries import (
    get_pending_users,
    get_vpns,
    get_user_by_id,
    update_item,
    get_all_servers,
    get_server_vpns,
    get_server,
    get_pending_bills
    )
from datetime import datetime, timedelta
from loader import bot, logger, config
import subprocess
from keyboards.reply import executed_user
from services.payment import check_bill, test_check_bill
from db.connect import session_maker


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

@logger.catch
async def update_server_config(server: Server):
    """ Генерирует конфиг сервера с пользователями,
    исключая пользователей с истекшим сроком подписки """

    vpns = get_server_vpns(server.id)
    with open(f'servers/instance/{server.name}_wg0.txt', 'r') as file:
        text = file.read()
        for vpn in vpns:
            if vpn.status != 'expired':
                text += f'\n#user_{vpn.user_id}\n'\
                        f'[Peer]\n'\
                        f'PublicKey = {vpn.public_key}\n'\
                        f'AllowedIPs = {vpn.ip}\n'
        with open(f"servers/{server.name}/wg0.conf", 'w') as conf:
            conf.write(text)
    logger.info(f'Конфигурация сервера {server.name} обновлена.')
    
@logger.catch
async def rebuild_server_config():
    logger.info('Запускаем обновление конфигурации на серверах...')
    servers = get_all_servers()
    for server in servers:
        await update_server_config(server)


@logger.catch
async def check_pending_users():
    logger.info('Проверка ожидающих пользователей...')
    data = get_pending_users()
    if data:
        logger.info('Есть ожидающие пользователи...')
        for item in data:
            vpn = item.get('vpn')
            user = item.get('user')
            user.status = 'executed'
            with open(f'users/qr/{user.id}.png', 'rb') as photo:
                await bot.send_message(user.telegram_id, 'Вот ваш QR код.\nНажмите "Инструкция" для получения подробных указаний по установке')
                await bot.send_photo(user.telegram_id, photo, reply_markup=executed_user)
            logger.info(f'Пользователь id={user.id} vpn_id={vpn[0].id} активирован')
            await rebuild_server_config()
            update_item(user)
    else:
        logger.info('Нет пользователей в очереди')

@logger.catch
async def check_pending_bills():
    logger.info('Проверка ожидающих счетов...')
    with session_maker() as session:
        vpns_bills = get_pending_bills()
        if vpns_bills:
            for vpn_bills in vpns_bills:
                bills_data = vpn_bills[1]
                vpn = vpn_bills[0]
                for bill_data in bills_data:
                    bill = bill_data.get('bill')
                    if check_bill(bill.label):
                        logger.info(f'Счет bill_id={bill.id} оплачен')
                        bill.status = 'paid'
                        bill.updated_at = datetime.now()
                        try:
                            await bot.delete_message(chat_id=bill.chat_id, message_id=bill.message_id)
                        except:
                            pass
                        await bot.send_message(chat_id=bill.chat_id, text=f'Ваш счет на сумму {bill_data.get("t_price")}₽. оплачен.')
                        if vpn.status == 'expired':
                            vpn.expires_at = datetime.now() + timedelta(days=bill_data.get('t_days'))
                        else:
                            vpn.expires_at += timedelta(days=bill_data.get('t_days'))
                        vpn.status = 'paid'
                        vpn.updated_at = datetime.now()
                        session.add(bill)
                    else:
                        bill.status = 'expired'
                        bill.updated_at = datetime.now()
                        try:
                            await bot.delete_message(chat_id=bill.chat_id, message_id=bill.message_id)
                        except:
                            pass
                        logger.info(f'Счет {bill.id} аннулирован')
                        session.add(bill)
                session.add(vpn)
            session.commit()
        else:
            logger.info('Нет ожидающих счетов')

async def check_server_config(server):
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
    with open(f'servers/{server.name}/wg0.conf', 'r') as file:
        local_wg0_config = file.read()
    if remote_sync_config.stdout == local_sync_config and remote_wg0_config.stdout == local_wg0_config:
        return True
    else:
        return False

async def check_config():
    servers = get_all_servers()
    for server in servers:
        if await check_server_config(server):
            logger.info(f'Конфигурация сервера {server.name}, ip: {server.wan_ip} актуальна')
        else:
            for admin in config.tg_bot.admin_ids:
                await bot.send_message(admin, f'Конфигурация не залилась на сервер {server.name}, ip: {server.wan_ip}')
            logger.warning(f'Конфигурация сервера {server.name}, ip: {server.wan_ip} не обновилась!')
