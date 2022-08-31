from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# создаем кнопки
reg = KeyboardButton('/Регистрация')
info = KeyboardButton('/Информация')
instruction = KeyboardButton('/Инструкция')
get_trial = KeyboardButton('/ПробнаяВерсия')
buy = KeyboardButton('/КупитьVPN')
profile = KeyboardButton('/МойПрофиль')
status = KeyboardButton('/СтатусVPN')
extend = KeyboardButton('/ПродлитьVPN')

# Создаем клавиатуру
start_new_user = ReplyKeyboardMarkup(resize_keyboard=True)
start_created_user = ReplyKeyboardMarkup(resize_keyboard=True)
start_executed_user = ReplyKeyboardMarkup(resize_keyboard=True)

# добавляем в нашу клавиатуру кнопки
start_new_user.row(reg, info)
start_created_user.row(get_trial).row(info, instruction).add(profile)
start_executed_user.add(extend).row(info, instruction).add(profile)
# add - друг под другом, insert - рядом если есть место
# есть еще метод .row(b1,b2) - все кнопки в ряд
