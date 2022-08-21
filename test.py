from datetime import datetime, timedelta


date1 = datetime.strptime('2022-08-21 15:37:06.736', '%Y-%m-%d %H:%M:%S.%f')
# date2 = datetime.strptime('2022-08-23 15:37:06.736', '%Y-%m-%d %H:%M:%S.%f')

date2 = date1 + timedelta(days=2)

print(date2)