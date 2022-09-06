import requests
import random
from db.models import Bill
from db.queries import create_bill
from datetime import datetime
from loader import logger

# def get_pay_url(price, user_id):
#     label = f'{user_id}_{random.randint(1,99999)}'
#     pay_url = f'https://yoomoney.ru/quickpay/confirm.xml?receiver=4100117941854976'\
#               f'&quickpay-form=shop&sum={price}&label={label}'
#     response = requests.post(pay_url)
#     return (response.url)

def get_pay_url(vpn, tariff):
    label = f'{vpn.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    pay_url = f'https://yoomoney.ru/quickpay/confirm.xml?receiver=4100117941854976'\
              f'&quickpay-form=shop&sum={tariff.price}&label={label}'
    create_bill(vpn.id, tariff.id, pay_url)
    return pay_url