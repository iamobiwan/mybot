from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from db.models import User, Vpn
from states import RegistrationStates
from db.queries.common import update_item
from keyboards.inline import (
    back_main
    )
from services.decorators import auth
from services.vpn import generate_user_config
from services.actions import send_settings
from loader import logger
from datetime import datetime


@logger.catch
@auth
async def get_settings_callback(callback: types.CallbackQuery, user, **kwargs):
    if user.vpn_status == 'not requested':
        await callback.message.edit_text(
            f'Мы получили Ваш запрос на формирование настроек.\n\n'\
            f'В течение 5 минут бот обработает Ваш запрос и пришлет настройки\n\n'
            f'Ожидайте...',
            parse_mode='Markdown',
            reply_markup=back_main()
            )
        generate_user_config(user)
    elif user.vpn_status == 'pending':
        await callback.message.edit_text(
            f'Ваши настройки формируются.\n\n'\
            f'В течение 5 минут бот обработает Ваш запрос и пришлет настройки\n\n'
            f'Ожидайте...',
            parse_mode='Markdown',
            reply_markup=back_main()
            )
    else:
        await send_settings(user)
        await callback.answer('Настройки отправлены')

@logger.catch
@auth
async def get_settings(message : types.Message, user, **kwargs):
    await message.delete()
    await send_settings(user)



def register_vpn_handlers(dp : Dispatcher):
    dp.register_callback_query_handler(get_settings_callback, text='get_settings')
    dp.register_message_handler(get_settings, commands=['getsettings'])