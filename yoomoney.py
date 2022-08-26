from random import randint
from dotenv import load_dotenv
import os
import requests
import random
from datetime import datetime, timedelta
import json
load_dotenv()

# client_id = os.getenv('CLIENT_ID')
# redirect_url = 'https://t.me/EnduranceVpnBot'
# scope = 'account-info operation-history operation-details incoming-transfers'

# url = f'https://yoomoney.ru/oauth/authorize?client_id={client_id}&response_type=code&'\
#       f'redirect_uri={redirect_url}&scope={scope}'
# headers = {
#     'Content-Type': 'application/x-www-form-urlencoded'
# }
# response = requests.post(url, headers=headers)
# print(response.url)

# pay_url = 'https://yoomoney.ru/quickpay/confirm.xml?receiver=4100117941854976&quickpay-form=shop&sum=2&label=5555'
# response = requests.post(pay_url)
# print(response.url)

token = os.getenv('Y_TOKEN')
url = f'https://yoomoney.ru/api/operation-history'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/x-www-form-urlencoded',
}
params = {
    # 'type': 'deposition',
    # 'records': 3,
    'label': '5555',
    # 'details': 'true'
    # 'operation_id': '714571374770005004'
}

# params = json.dumps(params)
response = requests.post(url, headers=headers, data=params)
print(response.json())


