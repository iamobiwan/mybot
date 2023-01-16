from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from db.models import User, Vpn
from states import RegistrationStates
from db.queries.users import create_user, get_user
from db.queries.common import update_item
from keyboards.inline import (
    plans_keyboard,
    start_keyboard,
    subscribed_user_keyboard,
    unsubscribed_keyboard,
    back_main
    )
from services.vpn import create_vpn
from services.decorators import auth
from loader import logger
from datetime import datetime, timedelta
import const


@logger.catch
@auth
async def start(message : types.Message, user, **kwagrs):
    text = f'Добро пожаловать, {message.from_user.full_name}!\n\n'\
        f'Этот бот предоставит Вам быстрый и безопасный доступ '\
        f'к сети Интернет при помощи VPN.\n\n'\
        f'Список команд доступен в меню бота внизу слева.\n'\
        f'Так же можете выполнить команду /help для вывода всех доступных для бота команд\n\n'
    if not user or user.status == 'created':
        text += f'Бот работает по подписке. Для создания VPN оформите подписку '\
                f'или активируйте пробный период.'
    else:
        text += f'Статус вашей подписки: {user.user_status}\n'
        if user.status == 'expired': 
            text += f'\nБот работает по подписке. Для использования VPN продлите подписку'
        else:
            text += f'Дата окончания: {user.expires_at.strftime("%d.%m.%Y")}'
    await message.answer(text, reply_markup=start_keyboard(user))

@logger.catch
@auth
async def main(message : types.Message, user, **kwagrs):
    if not user or user.status == 'created':
        await message.answer(
            f'Добро пожаловать, {message.from_user.full_name}!\n\n'\
            f'Для создания VPN оформите подписку '\
            f'или активируйте пробный период.',
            reply_markup=unsubscribed_keyboard(user)
            )
    else:
        text = f'Добро пожаловать, {message.from_user.full_name}!\n\n'\
            f'Выберите команду из списка ниже или нажмите "Меню" '\
            f'для того, чтобы увидеть весь список команд\n\n'\
            f'Статус вашей подписки: {user.user_status}\n'
        if user.status == 'expired': 
            text += f'\nБот работает по подписке. Для использования VPN продлите подписку'
        else:
            text += f'Дата окончания: {user.expires_at.strftime("%d.%m.%Y")}'
        await message.answer(text, reply_markup=subscribed_user_keyboard(user))

@logger.catch
@auth
async def main_callback(callback: types.CallbackQuery, user, **kwagrs):
    if not user or user.status == 'created':
        await callback.message.edit_text(
            f'Добро пожаловать, {callback.from_user.full_name}!\n\n'\
            f'Для создания VPN оформите подписку '\
            f'или активируйте пробный период.',
            reply_markup=unsubscribed_keyboard(user)
            )
    else:
        text = f'Добро пожаловать, {callback.from_user.full_name}!\n\n'\
            f'Выберите команду из списка ниже или нажмите "Меню" '\
            f'для того, чтобы увидеть весь список команд\n\n'\
            f'Статус вашей подписки: {user.user_status}\n'
        if user.status == 'expired': 
            text += f'\nБот работает по подписке. Для использования VPN продлите подписку'
        else:
            text += f'Дата окончания: {user.expires_at.strftime("%d.%m.%Y")}'
        await callback.message.edit_text(text, reply_markup=subscribed_user_keyboard(user))

@logger.catch
async def get_subscribe(callback: types.CallbackQuery):
    await callback.message.edit_text('Выберите длительность подписки:', reply_markup=plans_keyboard())

@logger.catch
@auth
async def activate_trial(callback: types.CallbackQuery, user, **kwagrs):
    if not user:
        user = create_user(callback.from_user.id, callback.from_user.full_name)
    if user.status == 'subscribed' or user.status == 'expired':
        await callback.message.edit_text(
        'Вы не можете активировать пробный период!',
        reply_markup=back_main()
    )
    else:
        user.status = 'trial'
        user.user_status = 'Пробный период'
        user.expires_at = datetime.now() + timedelta(days=const.TRIAL_SUBSCRIBE_DAYS)
        await callback.message.edit_text(
            f'Благодарю за активацию пробного периода!\n\n'\
            f'Пробный период заканчивается {user.expires_at.strftime("%d.%m.%Y")}',
            reply_markup=back_main()
        )
        update_item(user)

@logger.catch
@auth
async def instruction(message : types.Message, user, **kwargs):
    """ Выдает пользователю инструкцию из файла """
    with open('text/instruction.txt', 'r', encoding='utf-8') as instruction:
        text = instruction.read()
    await message.answer(text)

@logger.catch
async def info(message : types.Message, **kwargs):
    await message.answer('Информация о боте')


@logger.catch
async def commands_help(message : types.Message, **kwargs):
    with open('text/commands.txt', 'r', encoding='utf-8') as commands:
        text = commands.read()
    await message.answer(text)








def register_user_handlers(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(main, commands=['subscribe'])
    dp.register_callback_query_handler(main_callback, text='main_callback')
    dp.register_callback_query_handler(get_subscribe, text='get_subscribe')
    dp.register_callback_query_handler(activate_trial, text='activate_trial')
    dp.register_message_handler(instruction, commands=['instruction'])
    dp.register_message_handler(info, commands=['info'])
    dp.register_message_handler(commands_help, commands=['help'])
