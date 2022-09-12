import requests
import random
from loader import logger
from loader import config
from datetime import datetime, timedelta
from db.queries import update_item, get_pending_bills_data_by_vpn

def check_bill(label):
    url = f'https://yoomoney.ru/api/operation-history'
    headers = {
        'Authorization': f'Bearer {config.pay.y_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    params = {
        'label': label,
        # 'type': 'deposition',
        # 'records': 3,
        # 'details': 'true'
        # 'operation_id': '714571374770005004'
    }
    response = requests.post(url, headers=headers, data=params)
    try:
        operations = response.json().get('operations')
    except:
        operations = None
    if operations:
        if operations[0].get('status') == 'success':
            return True
    else:
        return False

def test_check_bill(label):
    return random.choice([True, False])

def check_pendig_user_bills(user, user_vpn):
    bills_data = get_pending_bills_data_by_vpn(user_vpn.id)
    if bills_data:
        for bill_data in bills_data:
            bill = bill_data.get('bill')
            tariff = bill_data.get('tariff')
            if test_check_bill(bill.label):
                bill.status = 'paid'
                bill.updated_at = datetime.now()
                logger.info(f'Счет пользователя user_id={user.id} vpn_id={user_vpn.id} bill_id={bill.id} оплачен')
                if user_vpn.status == 'expired':
                    user_vpn.expires_at = datetime.now() + timedelta(days=tariff.days)
                else:
                    user_vpn.expires_at += timedelta(days=tariff.days)
                logger.info(f'Срок действия VPN vpn_id={user_vpn.id} продлен на {tariff.days} дней,'\
                            f'заканчивается {user_vpn.expires_at.strftime("%d.%m.%Y")}')
                user_vpn.status = 'paid'
                user_vpn.updated_at = datetime.now()
                update_item(bill)
            else:
                logger.info(f'Счет пользователя user_id={user.id} vpn_id={user_vpn.id} bill_id={bill.id} НЕ оплачен')
        return user_vpn
    else:
        return user_vpn
