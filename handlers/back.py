from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from db.models import User, Vpn
from states import RegistrationStates
from db.queries.queries import (
    create_user,
    get_user,
    get_plan,
    create_bill,
    update_item
    )
from keyboards.inline import (
    plans_keyboard,
    pending_bills,
    start_keyboard,
    subscribed_user_keyboard
    )
from services.decorators import auth
from loader import logger

@logger.catch
@auth
async def back_main(callback: types.CallbackQuery, user):
    if not user or user.status == 'created':
        await callback.message.edit_text(
            f'Добро пожаловать, {callback.from_user.full_name}!\n\n'\
            f'Для создания VPN оформите подписку '\
            f'или активируйте пробный период.',
            reply_markup=start_keyboard(user)
            )
    else:
        await callback.message.edit_text(
            f'Добро пожаловать, {callback.from_user.full_name}!\n\n'\
            f'Выберите команду из списка ниже или нажмите "Меню" '\
            f'для того, чтобы увидеть весь список команд\n\n'\
            f'Статус вашей подписки: {user.user_status}\n'\
            f'Дата окончания: {user.expires_at}',
            reply_markup=subscribed_user_keyboard()
            )




def register_back_handlers(dp : Dispatcher):
    dp.register_callback_query_handler(back_main, text='back_main')