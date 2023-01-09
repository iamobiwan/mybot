from random import randint
from dotenv import load_dotenv
import os
import requests
import random
from datetime import datetime, timedelta
import json
load_dotenv()

secret = os.getenv('Q_SECRET_KEY')
public = os.getenv('Q_CLIENT_ID')

user_id = 123
bill_expires = datetime.now() + timedelta(days=1)
url = f'https://api.qiwi.com/partner/bill/v1/bills/{user_id}-{random.randint(1,99999)}'
headers = {
    'content-type': 'application/json',
    'accept': 'application/json',
    'Authorization': f'Bearer {secret}' 
}
params = {  
  "amount": {   
    "currency": "RUB",   
    "value": "1.00" 
   },  
  "comment": "Text comment",  
  "expirationDateTime": str(bill_expires.strftime('%Y-%m-%dT%H:%M:%S+03:00')), 
  "customer": {}, 
  "customFields" : {}
 }

params = json.dumps(params)

response = requests.put(url, data=params, headers=headers)
print(response.status_code)
print(response.text)