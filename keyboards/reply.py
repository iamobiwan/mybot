from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# создаем кнопки
reg = KeyboardButton('/Регистрация')
info = KeyboardButton('/Информация')
instruction = KeyboardButton('/Инструкция')
buy = KeyboardButton('/Получить VPN')
status = KeyboardButton('/Статус VPN')
extend = KeyboardButton('/Продлить VPN')

# Создаем клавиатуру
start_new_user = ReplyKeyboardMarkup(resize_keyboard=True)
start_created_user = ReplyKeyboardMarkup(resize_keyboard=True)
start_executed_user = ReplyKeyboardMarkup(resize_keyboard=True)

# добавляем в нашу клавиатуру кнопки
start_new_user.row(reg, info)
start_created_user.row(info, buy, instruction)
start_executed_user.row(info, status, instruction)
# add - друг под другом, insert - рядом если есть место
# есть еще метод .row(b1,b2) - все кнопки в ряд
