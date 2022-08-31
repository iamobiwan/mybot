import asyncio
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from db.models import User, Vpn
from states import RegistrationStates
from db.queries import create_user, get_user_data, get_tariff
from keyboards.reply import start_new_user, start_created_user, start_executed_user
from keyboards.inline import tariffs_keyboard, pay_keyboard, tariffs_cd
from services.vpn import generate_user_config, create_vpn, choose_server
from services.payment import get_pay_url
from services.decorators import auth
from loader import dp

async def start(message : types.Message):
    """ Старт бота, проверка регистрации пользователя """
    data = get_user_data(message.from_user.id)
    if data:
        user = data.get('user')
        if user.status == 'created':
            await message.answer(
                f'Привет, {user.name}! Что делаем?',
                reply_markup=start_created_user
                )
        else:
            await message.answer(
                f'Привет, {user.name}! Что делаем?',
                reply_markup=start_executed_user
                )
    else:
        await message.answer(
            'Привет! Нужен VPN? Зарегистрируйся!',
            reply_markup=start_new_user)

async def register(message : types.Message):
    data = get_user_data(message.from_user.id)
    if data:
        await message.answer('Вы уже зарегистрированы!')
    else:
        await message.answer('Укажите имя', reply_markup=ReplyKeyboardRemove())
        await RegistrationStates.name.set()

async def register_set_name(message : types.Message, state: FSMContext):
    """ Регистрация пользователей после проверки имени """
    name = message.text
    if len(name) > 15:  # Проверка на длину имени
        await message.answer(f'Имя слишком длинное, попробуй еще.')
        await RegistrationStates.name.set()
    elif "/" in name or "@" in name:
        await message.answer(f'Имя содержит не допустимые символы, попробуй еще.')
        await RegistrationStates.name.set()
    else:
        create_user(message.from_user.id, name)
        await message.answer(f'Регистрация завершена, {name}!', reply_markup=start_created_user)
        await state.finish()

@auth
async def profile(message : types.Message, data, **kwargs):
    user = data.get('user')
    user_vpn: Vpn = data.get('vpn')
    text = f'Ваше имя: {user.name}\n'
    if not user_vpn:
        text += f'Статус вашего VPN: Не создан'
    elif user.status == 'pending':
        text += f'Статус вашего VPN: В обработке'
    elif user_vpn.status == 'paid':
        text += f'Статус вашего VPN: "Оплачен"\n'\
                f'Срок действия заканчивается: {user_vpn.expires_at.strftime("%d.%m.%Y")}'
    elif user_vpn.status == 'expired':
        text += f'Статус вашего VPN: "Истек"\n'
    elif user_vpn.status == 'trial':
        text += f'Статус вашего VPN: "Пробный"\n'\
                f'Срок действия заканчивается: {user_vpn.expires_at.strftime("%d.%m.%Y")}'
    await message.answer(text)

@auth
async def instruction(message : types.Message, data, **kwargs):
    with open('text/instruction.txt', 'r') as instruction:
        text = instruction.read()
    await message.answer(text)

async def get_vpn_trial(message: types.Message):
    data = get_user_data(message.from_user.id)
    user = data.get('user')
    user_id = user.id
    if data:
        await message.answer(f'Пробная версия выдается на 3 дня.\n'\
                             f'Статус твоего аккаунта можно посмотреть\n'\
                             f'по кнопке "МойПрофиль"')
        server = choose_server()
        if server:
            if user.status == 'created':
                result = create_vpn(user, server)
                if result:
                    await message.answer('Получили Ваш запрос.\nОжидайте формирования настроек.\nОбычно занимает около 5 минут.')
                else:
                    await message.answer('Что-то пошло не так')
            else:
                await message.answer('Для вас уже создан VPN', reply_markup=start_executed_user)
        else:
            await message.answer('Нет свободных серверов', reply_markup=start_created_user)
    else:
        await message.answer('Вы не зарегистрированы', reply_markup=start_new_user)

@auth
async def buy_vpn(message: types.Message, data, **kwargs):
    await message.answer('Выберите тарифный план:', reply_markup=tariffs_keyboard())

async def pay(callback: types.CallbackQuery, callback_data: dict):
    tariff_id = callback_data.get('id')
    tariff = get_tariff(tariff_id)
    data = get_user_data(callback.from_user.id)
    user = data.get('user')
    await callback.message.edit_text(f'Подождите, формируется счет...')
    pay_url = get_pay_url(tariff.price, user.id)
    await callback.message.edit_text(f'Выбран тариф {tariff.name}', reply_markup=pay_keyboard(pay_url))

async def cancel_bill(callback: types.CallbackQuery):
    await callback.message.edit_text('Выберите тарифный план:', reply_markup=tariffs_keyboard())

async def cancel_buy(callback: types.CallbackQuery):
    await callback.message.delete()


def register_user_handlers(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(register, commands=['Регистрация'])
    dp.register_message_handler(register_set_name, state=RegistrationStates.name)
    dp.register_message_handler(buy_vpn, commands=['КупитьVPN', 'ПродлитьVPN'])
    dp.register_message_handler(get_vpn_trial, commands=['ПробнаяВерсия'])
    dp.register_message_handler(instruction, commands=['Инструкция'])
    dp.register_message_handler(profile, commands=['МойПрофиль'])
    dp.register_callback_query_handler(pay, tariffs_cd.filter(tariff='tariff'))
    dp.register_callback_query_handler(cancel_bill, text='cancel_bill')
    dp.register_callback_query_handler(cancel_buy, text='cancel_buy')