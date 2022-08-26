from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from db.queries import get_all_tariffs

tariffs_cd = CallbackData('vpn', 'tariff', 'id')

def make_tariff_cd(id):
    return tariffs_cd.new(tariff='tariff',id=id)

def tariffs_keyboard():
    markup = InlineKeyboardMarkup()
    tariffs = get_all_tariffs()
    for tariff in tariffs:
        button_text = f'Тариф {tariff.name} на {tariff.days} дней'
        markup.row(
            InlineKeyboardButton(text=button_text, callback_data = make_tariff_cd(tariff.id))
        )
    markup.row(
        InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel_buy'
        )
    )
    return markup

def pay_keyboard(pay_url):
    markup = InlineKeyboardMarkup()
    bill = InlineKeyboardButton(text='Оплатить', url=pay_url)
    markup.insert(bill)
    markup.row(
        InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_bill'
            )
    )
    return markup