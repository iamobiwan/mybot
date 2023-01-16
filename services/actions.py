from db.models import Server, User
from db.queries.vpn import (
    get_vpns,
    get_all_servers,
    get_server_vpns,
    get_server,
    get_pending_users
    )
from db.queries.common import update_item
from db.queries.users import get_user_by_id, get_users
from db.queries.orders import get_pending_orders
from keyboards.inline import subscribed_user_keyboard, subcribe_notification
from datetime import datetime, timedelta
from loader import bot, logger, config
from services.donate import check_order, test_check_order
from services.sync import sync_config, check_config
from db.connect import session_maker
from db.models import Order
import const


@logger.catch
async def check_sub_expire():
    logger.info('Запускаем проверку на истечение срока подписки...')
    users = get_users()
    date = datetime.now()
    for user in users:
        if user.status == 'trial' or user.status == 'subscribed':
            if date > user.expires_at:
                # user = get_user_by_id(vpn.user_id)
                logger.info(f'У пользователя {user.id} {user.name} истек срок действия VPN (был {user.status})')
                user.status = 'expired'
                user.user_status = 'Подписка закончилась'
                await bot.send_message(
                    user.telegram_id,
                    f'Срок действия Вашей подписки истек. \U00002639\n\n'\
                    f'Чтобы продолжить пользоваться VPN продлите подписку',
                    reply_markup=subscribed_user_keyboard(user)    
                        )
                update_item(user)
            else:
                diff: timedelta = user.expires_at - date
                if diff.days in const.SUB_DAYS_LEFT:
                    await bot.send_message(
                    user.telegram_id,
                    f'Срок действия Вашей подписки скоро закончится.\n'\
                    f'Дата окончания: {user.expires_at.strftime("%d.%m.%Y")}\n\n'
                    f'Чтобы продолжить пользоваться VPN продлите подписку',
                    reply_markup=subcribe_notification()    
                        )

@logger.catch
async def update_server_config(server: Server):
    """ Генерирует конфиг сервера с пользователями,
    исключая пользователей с истекшим сроком подписки """
    vpns = get_server_vpns(server.id)
    with open(f'servers/instance/{server.name}_wg0.txt', 'r') as file:
        text = file.read()
        for vpn in vpns:
            user = get_user_by_id(vpn.user_id)
            if user.status != 'expired':
                text += f'\n#user_{vpn.user_id}\n'\
                        f'[Peer]\n'\
                        f'PublicKey = {vpn.public_key}\n'\
                        f'AllowedIPs = {vpn.ip}\n'
        with open(f"servers/{server.name}/wg0.conf", 'w') as conf:
            conf.write(text)
    logger.info(f'Конфигурация сервера {server.name} сгенерирована.')
    
@logger.catch
async def rebuild_server_config():
    logger.info('Запускаем обновление конфигурации на серверах...')
    servers = get_all_servers()
    for server in servers:
        await update_server_config(server)
        await sync_config(server)
        await check_config(server)

@logger.catch
async def check_pending_users():
    logger.info('Проверка ожидающих пользователей...')
    pending_users = get_pending_users()
    if pending_users:
        logger.info('Есть ожидающие пользователи...')
        for user in pending_users:
            await send_settings(user)
            user.vpn_status = 'activated'
            update_item(user)
        await rebuild_server_config()
    else:
        logger.info('Нет пользователей в очереди')

@logger.catch
async def send_settings(user):
    with open(f'users/qr/{user.id}.png', 'rb') as photo:
        await bot.send_message(
            user.telegram_id,
            'Вот ваши настройки в виде QR кода.\n\n'\
            'Нажмите /instruction для получения подробных указаний по установке'
            )
        await bot.send_photo(user.telegram_id, photo)
        logger.info(f'Пользователь ID {user.id} получил свои настройки')

@logger.catch
async def check_pending_orders():
    logger.info('Проверка ожидающих счетов...')
    with session_maker() as session:
        orders = session.query(Order).filter(
            Order.status == 'pending',
            ).all()
        for order in orders:
            if test_check_order(order):
                order.status = 'success'
                order.user_status = 'оплачен'
                order.updated_at = datetime.now()
                if order.user.status in ['expired','created']:
                    order.user.expires_at = datetime.now() + timedelta(days=order.plan_days)
                else:
                    order.user.expires_at += timedelta(days=order.plan_days)
                order.user.status = 'subscribed'
                order.user.user_status = 'Подписка оформлена'
                order.user.updated_at = datetime.now()
                await bot.send_message(
                    chat_id=order.user.telegram_id,
                    text=f'Ваш счет {order.id} на сумму {order.amount}₽. оплачен.\n\n'\
                        f'Статус вашей подписки: {order.user.user_status}\n'\
                        f'Дата окончания: {order.user.expires_at.strftime("%d.%m.%Y")}'
                        )
                session.add(order)
            else:
                diff:timedelta = datetime.now() - order.created_at
                if diff.days > const.PENDING_ORDER_TTL:
                    order.delete()
                    await bot.send_message(
                        chat_id=order.user.telegram_id,
                        text=f'Ваш счет {order.id} на сумму {order.amount}₽ удален.\n\n'
                        )
                elif diff.days == const.PENDING_ORDER_NOTIFICATION:
                    await bot.send_message(
                        chat_id=order.user.telegram_id,
                        text=f'Ваш счет {order.id} на сумму {order.amount}₽ в статусе {order.user_status} скоро будет удален.\n\n'
                        )
            session.commit()

    # with session_maker() as session:
    #     vpns_bills = get_pending_bills()
    #     if vpns_bills:
    #         for vpn_bills in vpns_bills:
    #             bills_data = vpn_bills[1]
    #             vpn = vpn_bills[0]
    #             for bill_data in bills_data:
    #                 bill = bill_data.get('bill')
    #                 if test_check_bill(bill.label):
    #                     logger.info(f'Счет bill_id={bill.id} оплачен')
    #                     bill.status = 'paid'
    #                     bill.updated_at = datetime.now()
    #                     try:
    #                         await bot.delete_message(chat_id=bill.chat_id, message_id=bill.message_id)
    #                     except:
    #                         pass
    #                     await bot.send_message(chat_id=bill.chat_id, text=f'Ваш счет на сумму {bill_data.get("t_price")}₽. оплачен.')
    #                     if vpn.status == 'expired':
    #                         vpn.expires_at = datetime.now() + timedelta(days=bill_data.get('t_days'))
    #                     else:
    #                         vpn.expires_at += timedelta(days=bill_data.get('t_days'))
    #                     vpn.status = 'paid'
    #                     vpn.updated_at = datetime.now()
    #                     session.add(bill)
    #                 else:
    #                     bill.status = 'expired'
    #                     bill.updated_at = datetime.now()
    #                     try:
    #                         await bot.delete_message(chat_id=bill.chat_id, message_id=bill.message_id)
    #                     except:
    #                         pass
    #                     logger.info(f'Счет {bill.id} аннулирован')
    #                     session.add(bill)
    #             session.add(vpn)
    #         session.commit()
    #     else:
    #         logger.info('Нет ожидающих счетов')
