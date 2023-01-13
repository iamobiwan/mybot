from aiogram import Dispatcher, types
from db.queries.orders import (
    create_order,
    get_order,
    get_user_orders,
    delete_order
    )
from db.queries.users import (
    create_user,
    get_user,
)
from db.queries.plan import get_plan
from keyboards.inline import (
    donate_keyboard,
    orders_keyboard,
    back_main
    )
from keyboards.callback import plan_callback, order_callback
from services.decorators import auth
from loader import logger
import const

@logger.catch
async def donate_subscription(callback: types.CallbackQuery, callback_data: dict):
    plan = get_plan(callback_data.get('plan_id'))
    user = get_user(callback.from_user.id)
    if not user:
        user = create_user(callback.from_user.id, callback.from_user.full_name)
    if len(get_user_orders(user.id)) <= const.MAX_ORDERS_CNT:
        order = create_order(user, plan)
        await callback.message.edit_text(
            f'Ваш заказ *№{order.id}*\n'\
            f'Cумма: *{plan.amount}₽*\n'\
            f'Количество дней: *{plan.days}*\n'\
            f'Статус: *{order.user_status}*\n'\
            f'Заказ действителен до конца дня.',
            parse_mode='Markdown',
            reply_markup=donate_keyboard(order, callback))
    else:
        await callback.message.edit_text(
            f'У вас максимальное количество заказов.\n'\
            f'Удалите или оплатите имеющиеся заказы',
            reply_markup=back_main())

@logger.catch
@auth
async def show_orders(callback: types.CallbackQuery, user, **kwagrs):
    await callback.message.edit_text(
        f'*Ваши заказы*\n\nНеоплаченные заказы автоматически '\
        f'удаляются через 24 часа',
        parse_mode='Markdown',
        reply_markup=orders_keyboard(user)
        )

@logger.catch
@auth
async def show_order(callback: types.CallbackQuery, user, callback_data: dict, **kwargs):
    order = get_order(callback_data.get('order_id'))
    await callback.message.edit_text(
        f'Детали заказа *№{order.id}*\n\n'\
        f'Статус: *{order.user_status}*\n'\
        f'Создан: *{order.created_at.strftime("%d.%m.%Y %H:%M")} МСК*\n\n'\
        f'По вопросам оплаты заказа обращайтесь @endurancevpnsupport',
        parse_mode='Markdown',
        reply_markup=donate_keyboard(order, callback)
        )

async def remove_order(callback: types.CallbackQuery, callback_data: dict):
    delete_order(callback_data.get('order_id'))
    await callback.answer('Заказ удален')
    await show_orders(callback)


def register_donate_handlers(dp : Dispatcher):
    dp.register_callback_query_handler(donate_subscription, plan_callback.filter())
    dp.register_callback_query_handler(show_orders, text='show_orders')
    dp.register_callback_query_handler(show_order, order_callback.filter(action='get'))
    dp.register_callback_query_handler(remove_order, order_callback.filter(action='delete'))