import requests
from dotenv import load_dotenv
import os

load_dotenv()
client_id = os.getenv('CLIENT_ID')
code = '3703805477E9C23816C58B9ABD9F7F933A0A77B62C5C49845D3232A8B85A203FF2F6B866474279F45A9CE0678C048348AF5679785937AC148300DC60FE9DA7B38E8374023B3FBEB4C611A857C42F8661A8ED7C959845A7E34B02011B21FE1EE1438232759E635E84741E56A6CA1011F6130291CB2EB3C78DAA7238934BCD46AB'
redirect_url = 'https://t.me/EnduranceVpnBot'
url = f'https://yoomoney.ru/oauth/token?code={code}&client_id={client_id}&'\
      f'grant_type=authorization_code&redirect_uri={redirect_url}'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}
# print(url)
response = requests.post(url, headers=headers)
print(response.text)