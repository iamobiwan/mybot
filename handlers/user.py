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
    await message.delete()
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
    await message.delete()
    with open('text/instruction.txt', 'r') as instruction:
        text = instruction.read()
    await message.answer(text)








def register_user_handlers(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(main, commands=['subscribe'])
    dp.register_callback_query_handler(main_callback, text='main_callback')
    dp.register_callback_query_handler(get_subscribe, text='get_subscribe')
    dp.register_callback_query_handler(activate_trial, text='activate_trial')
    dp.register_message_handler(instruction, commands=['instruction'])
    # dp.register_message_handler(register, commands=['Регистрация'])
    # dp.register_message_handler(register_set_name, state=RegistrationStates.name)
    # dp.register_message_handler(buy_vpn, commands=['ПродлитьVPN'])
    # dp.register_message_handler(get_vpn_trial, commands=['ПробнаяВерсия'])
    # dp.register_message_handler(information, commands=['Информация'])
    # dp.register_message_handler(profile, commands=['МойПрофиль'])
    # dp.register_message_handler(orders, commands=['МоиСчета'])
    # dp.register_callback_query_handler(back_tariff, text='back_tariff')
    # dp.register_callback_query_handler(cancel_buy, text='cancel_buy')


# @logger.catch
# @auth
# async def profile(message : types.Message, data, **kwargs):
#     """
#         Возвращает статус профиля и статус VPN пользователя.
#         Данные пользователя возвращаются из декоратора в параметре "data"
#     """
#     user: User = data.get('user')
#     user_vpn: Vpn = data.get('vpn')
#     text = f'Ваше имя: {user.name}\n'\
#            f'Ваш ID: {user.id}\n'
#     if user_vpn:
#         user_vpn = await check_pendig_user_orders(user, user_vpn)
#         if user.status == 'pending':
#             text += f'Статус вашего VPN: В обработке'
#         elif user_vpn.status == 'paid':
#             text += f'Статус вашего VPN: "Оплачен"\n'\
#                     f'Срок действия заканчивается: {user_vpn.expires_at.strftime("%d.%m.%Y")}'
#         elif user_vpn.status == 'expired':
#             text += f'Статус вашего VPN: "Истек"\n'
#         elif user_vpn.status == 'trial':
#             text += f'Статус вашего VPN: "Пробный"\n'\
#                     f'Срок действия заканчивается: {user_vpn.expires_at.strftime("%d.%m.%Y")}'
#         update_item(user_vpn)
#     else:
#         text += 'Статус вашего VPN: Не создан'    
#     await message.answer(f'{text}')

# @logger.catch
# async def start(message : types.Message):
#     """ Старт бота, проверка регистрации пользователя """
#     data = get_user_data(message.from_user.id)
#     if data:
#         user = data.get('user')
#         if user.status == 'created':
#             await message.answer(
#                 f'Привет, {user.name}! Что делаем?',
#                 reply_markup=created_user
#                 )
#         elif user.status == 'pending':
#             await message.answer(
#                 f'Привет, {user.name}! Что делаем?',
#                 reply_markup=pending_user
#                 )
#         else:
#             await message.answer(
#                 f'Привет, {user.name}! Что делаем?',
#                 reply_markup=executed_user
#                 )
#     else:
#         await message.answer(
#             'Добро пожаловать на главную страницу. Выберите действие:',
#             reply_markup=new_user)

# @logger.catch
# async def register(message : types.Message):
#     """ 
#         После ввода имени, активирует хендлер "register_set_name",
#         фиксируя имя через FSM
#     """
#     data = get_user(message.from_user.id)
#     if data:
#         await message.answer('Вы уже зарегистрированы!')
#     else:
#         await message.answer('Укажите имя', reply_markup=ReplyKeyboardRemove())
#         await RegistrationStates.name.set()

# @logger.catch
# async def register_set_name(message : types.Message, state: FSMContext):
#     """ Регистрация пользователей после проверки имени """
#     name = message.text
#     if len(name) > 15:  # Проверка на длину имени
#         logger.warning(f'Пользователь с telegram ID {message.from_user.id} ввел слишком длинное имя')
#         await message.answer(f'Имя слишком длинное, попробуй еще.')
#         await RegistrationStates.name.set()
#     elif "/" in name or "@" in name:
#         logger.warning(f'Пользователь с telegram ID {message.from_user.id} ввел не корректное имя')
#         await message.answer(f'Имя содержит не допустимые символы, попробуй еще.')
#         await RegistrationStates.name.set()
#     else:
#         create_user(message.from_user.id, name)
#         await message.answer(f'Регистрация завершена, {name}!', reply_markup=created_user)
#         await state.finish()



# @logger.catch
# async def information(message:types.Message):
#     await message.answer(f'Информация')

# @logger.catch
# @auth
# async def instruction(message : types.Message, data, **kwargs):
#     """ Выдает пользователю инструкцию из файла """
#     with open('text/instruction.txt', 'r') as instruction:
#         text = instruction.read()
#     await message.answer(text)

# @logger.catch
# @auth
# async def get_vpn_trial(message: types.Message, data, **kwargs):
#     """ Создает trial vpn на 3 дня для тестирования пользователем """
#     user = data.get('user')
#     logger.info(f'Получен запрос на пробный VPN от пользователя {user.id}')
#     await message.answer(f'Пробная версия выдается на 3 дня.\n'\
#                             f'Статус своего аккаунта можно посмотреть\n'\
#                             f'по кнопке "МойПрофиль"')
#     if user.status == 'created':
#         result = create_vpn(user)
#         if result:
#             await message.answer('Получили Ваш запрос.\nОжидайте формирования настроек.\nОбычно занимает около 5 минут.',
#             reply_markup=pending_user)
#         else:
#             await message.answer('Что-то пошло не так, обратитесь в техническую поддержку @endurancevpnsupport')
#     else:
#         await message.answer('Для вас уже создан VPN', reply_markup=executed_user)

# @logger.catch
# @auth
# async def buy_vpn(message: types.Message, data, **kwargs):
#     await message.answer('Выберите тарифный план:', reply_markup=plans_keyboard())

# @logger.catch
# async def back_tariff(callback: types.CallbackQuery):
#     await callback.message.edit_text('Выберите тарифный план:', reply_markup=plans_keyboard())

# @logger.catch
# async def cancel_buy(callback: types.CallbackQuery):
#     await callback.message.delete()