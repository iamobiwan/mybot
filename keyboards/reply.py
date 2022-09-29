from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# создаем кнопки
reg = KeyboardButton('/Регистрация')
info = KeyboardButton('/Информация')
instruction = KeyboardButton('/Инструкция')
get_trial = KeyboardButton('/ПробнаяВерсия')
profile = KeyboardButton('/МойПрофиль')
status = KeyboardButton('/СтатусVPN')
extend = KeyboardButton('/ПродлитьVPN')
# bills = KeyboardButton('/МоиСчета')

# Создаем клавиатуру
new_user = ReplyKeyboardMarkup(resize_keyboard=True)
created_user = ReplyKeyboardMarkup(resize_keyboard=True)
executed_user = ReplyKeyboardMarkup(resize_keyboard=True)
pending_user = ReplyKeyboardMarkup(resize_keyboard=True)

# добавляем в нашу клавиатуру кнопки
new_user.row(reg, info)
created_user.row(get_trial).row(info).add(profile)
executed_user.add(extend).row(info, instruction).row(profile)
pending_user.add(info).row(profile)
# add - друг под другом, insert - рядом если есть место
# есть еще метод .row(b1,b2) - все кнопки в ряд
