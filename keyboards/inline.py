from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.queries.plan import get_all_plans
from db.queries.orders import get_user_orders
from .callback import plan_callback, order_callback


def  start_keyboard(user):
    if not user or user.status == 'created':
        return unsubscribed_keyboard(user)
    else:
        return subscribed_user_keyboard(user)


def unsubscribed_keyboard(user):
    activate_trial_button = InlineKeyboardButton(text='\U0000231B Активировать пробный период', callback_data = 'activate_trial')
    get_subscribe_button = InlineKeyboardButton(text='\U00002b50 Оформить подписку', callback_data = 'get_subscribe')
    promocode_button = InlineKeyboardButton(text='\U0001f91d Применить промокод', callback_data = 'apply_promocode')
    orders_button = InlineKeyboardButton(text='\U0001f4cb Мои заказы', callback_data = 'show_orders')
    
    markup = InlineKeyboardMarkup()
    markup.row(activate_trial_button)
    markup.row(get_subscribe_button)
    if user:
        orders = get_user_orders(user.id)
        if orders:
            markup.row(orders_button)
    else:
        markup.row(promocode_button)
    return markup


def subscribed_user_keyboard(user):
    markup = InlineKeyboardMarkup()
    if user.status != 'expired':
        markup.row(
            InlineKeyboardButton(
                text='\U0001f527 Получить настройки',
                callback_data='get_settings'
            )
        )
        markup.row(
            InlineKeyboardButton(
                text='\U0001f91d Мой промокод',
                callback_data='get_promocode'
            )
        )
    markup.row(
        InlineKeyboardButton(
            text='\U00002b50 Продлить подписку',
            callback_data='get_subscribe'
        )
    )
    orders = get_user_orders(user.id)
    if orders:
        markup.row(
            InlineKeyboardButton(
                text='\U0001f4cb Мои заказы',
                callback_data='show_orders'
            )
    )
    return markup

def subcribe_notification():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text='\U00002b50 Продлить подписку',
            callback_data='get_subscribe'
        )
    )
    return markup

def back_main():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text='\U000025c0 Назад',
            callback_data='main_callback'
        )
    )
    return markup

def plans_keyboard(user):
    markup = InlineKeyboardMarkup()
    plans = get_all_plans()
    for plan in plans:
        if user.discount:
            button_text = f'{plan.days} дней за {plan.amount - user.discount}₽ (было {plan.amount}₽)'
        else:
            button_text = f'{plan.days} дней за {plan.amount}₽'
        markup.row(
            InlineKeyboardButton(text=button_text, callback_data=plan_callback.new(plan_id=plan.id))
        )
    markup.row(
        InlineKeyboardButton(
            text='\U000025c0 Назад',
            callback_data='main_callback',
        )
    )
    return markup

def donate_keyboard(order, callback):
    markup = InlineKeyboardMarkup()
    if order.status != 'success':
        markup.insert(InlineKeyboardButton(text='\U0001f4b0 Донатить', url=order.donate_url))
    markup.row(InlineKeyboardButton(text='\U0001f5d1 Удалить', callback_data=order_callback.new(action='delete', order_id=order.id)))
    if 'plan' in callback.data:
        markup.row(
        InlineKeyboardButton(
                text='\U000025c0 Назад',
                callback_data='main_callback'
            )
    )
    else:
        markup.row(
            InlineKeyboardButton(
                    text='\U000025c0 Назад',
                    callback_data='show_orders'
                )
        )
    return markup

def orders_keyboard(user):
    orders = get_user_orders(user.id)
    markup = InlineKeyboardMarkup()
    if orders:
        for order in orders:
            if order.status == 'success':
                smile = '\U00002705'
            else:
                smile = '\U0000231b'
            button_text = f'{smile} №{order.id} от {order.created_at.strftime("%d.%m.%Y %H:%M")} МСК {order.amount}₽'
            markup.row(
                InlineKeyboardButton(text=button_text, callback_data=order_callback.new(action='get', order_id=order.id))
            )
    markup.row(
        InlineKeyboardButton(
            text='\U000025c0 Назад',
            callback_data='main_callback'
        )
    )
    return markup