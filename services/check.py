from db.models import User
from db.queries import get_trial_vpns, get_user_by_id
from datetime import datetime

async def check_user_status():
    pass
    # vpns = get_trial_vpns()
    # date = datetime.now()
    # for vpn in vpns:
    #     # expire_date = datetime.strptime(vpn.expires_at, '%Y-%m-%d %H:%M:%S.%f')
    #     # print(date, vpn.expires_at)
    #     if date > vpn.expires_at:
    #         user = get_user_by_id(vpn.user_id)
    #         print(f'У пользователя {user.name} закончился пробный период')
    #     else:
    #         print('Все пользователи активны')

    