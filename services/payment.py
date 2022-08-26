import requests
import random

def get_pay_url(price, user_id):
    label = f'{user_id}_{random.randint(1,99999)}'
    pay_url = f'https://yoomoney.ru/quickpay/confirm.xml?receiver=4100117941854976'\
              f'&quickpay-form=shop&sum={price}&label={label}'
    response = requests.post(pay_url)
    return (response.url)