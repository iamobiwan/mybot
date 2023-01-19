import requests
import random
from loader import logger, config, bot
from datetime import datetime, timedelta
from db.queries.common import update_item

def check_order(order):
    url = f'https://yoomoney.ru/api/operation-history'
    headers = {
        'Authorization': f'Bearer {config.donate.y_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    params = {
        'label': order.id,
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
            logger.info(f'Счет {order.id} оплачен.')
            return True
    else:
        return False

def test_check_order(order):
    logger.info(f'Счет {order.id} оплачен.')
    return True