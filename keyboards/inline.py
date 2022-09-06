from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from db.queries import get_all_tariffs, get_bill

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

def pay_keyboard(bill_id):
    bill = get_bill(bill_id)
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text='Оплатить', url=bill.pay_url)
    markup.insert(btn)
    markup.row(
        InlineKeyboardButton(
                text='Назад',
                callback_data='back_tariff'
            )
    )
    markup.row(
        InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel_buy'
            )
    )
    return markup

def pending_bills(bills_data):
    markup = InlineKeyboardMarkup()
    for bill_data in bills_data:
        tariff = bill_data.get('tariff')
        bill = bill_data.get('bill')
        text = f'Оплата тарифа "{tariff.name}" на сумму {tariff.price}р'
        btn = InlineKeyboardButton(text=text, url=bill.pay_url)
        markup.row(btn)
    return markup