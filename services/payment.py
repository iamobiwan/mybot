import requests
from loader import logger
from loader import config


# def get_pay_url(vpn, tariff):
#     label = f'{vpn.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
#     pay_url = f'https://yoomoney.ru/quickpay/confirm.xml?receiver={config.pay.y_wallet}'\
#               f'&quickpay-form=shop&sum={tariff.price}&label={label}'
#     create_bill(vpn.id, tariff.id, pay_url)
#     return pay_url

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
        print('Счет не оплачен')