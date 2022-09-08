from datetime import datetime, timedelta
from itertools import count
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from db.models import User, Vpn
from states import RegistrationStates
from db.queries import create_user, get_user_data, get_tariff, create_bill, get_bill, get_pending_bills_data_by_vpn, update_item
from keyboards.reply import start_new_user, start_created_user, start_executed_user
from keyboards.inline import tariffs_keyboard, pay_keyboard, tariffs_cd, pending_bills
from services.vpn import create_vpn, choose_server
from services.payment import check_bill
from services.decorators import auth
from loader import logger
import const

@logger.catch
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

@logger.catch
async def register(message : types.Message):
    """ 
        После ввода имени, активирует хендлер "register_set_name",
        фиксируя имя через FSM
    """
    data = get_user_data(message.from_user.id)
    if data:
        await message.answer('Вы уже зарегистрированы!')
    else:
        await message.answer('Укажите имя', reply_markup=ReplyKeyboardRemove())
        await RegistrationStates.name.set()

@logger.catch
async def register_set_name(message : types.Message, state: FSMContext):
    """ Регистрация пользователей после проверки имени """
    name = message.text
    if len(name) > 15:  # Проверка на длину имени
        logger.warning(f'Пользователь с telegram ID {message.from_user.id} ввел слишком длинное имя')
        await message.answer(f'Имя слишком длинное, попробуй еще.')
        await RegistrationStates.name.set()
    elif "/" in name or "@" in name:
        logger.warning(f'Пользователь с telegram ID {message.from_user.id} ввел не корректное имя')
        await message.answer(f'Имя содержит не допустимые символы, попробуй еще.')
        await RegistrationStates.name.set()
    else:
        create_user(message.from_user.id, name)
        await message.answer(f'Регистрация завершена, {name}!', reply_markup=start_created_user)
        await state.finish()

@logger.catch
@auth
async def profile(message : types.Message, data, **kwargs):
    """
        Возвращает статус профиля и статус VPN пользователя.
        Данные пользователя возвращаются из декоратора в параметре "data"
    """
    user: User = data.get('user')
    user_vpn: Vpn = data.get('vpn')
    bills_data = get_pending_bills_data_by_vpn(user_vpn.id)
    if bills_data:
        for bill_data in bills_data:
            bill = bill_data.get('bill')
            tariff = bill_data.get('tariff')
            if check_bill(bill.label):
                bill.status == 'paid'
                update_item(bill)
                if user_vpn.status == 'expired':
                    user_vpn.expires_at = datetime.now() + timedelta(days=tariff.days)
                else:
                    user_vpn.expires_at += timedelta(days=tariff.days)
                user_vpn.status = 'paid'
                user_vpn.updated_at = datetime.now() 

    text = f'Ваше имя: {user.name}\n'\
           f'Ваш ID: {user.id}\n'
    if not user_vpn:
        text += f'Статус вашего VPN: Не создан'
    elif user_vpn.status == 'pending':
        text += f'Статус вашего VPN: В обработке'
    elif user_vpn.status == 'paid':
        text += f'Статус вашего VPN: "Оплачен"\n'\
                f'Срок действия заканчивается: {user_vpn.expires_at.strftime("%d.%m.%Y")}'
    elif user_vpn.status == 'expired':
        text += f'Статус вашего VPN: "Истек"\n'
    elif user_vpn.status == 'trial':
        text += f'Статус вашего VPN: "Пробный"\n'\
                f'Срок действия заканчивается: {user_vpn.expires_at.strftime("%d.%m.%Y")}'
    update_item(user_vpn)
    await message.answer(text)

@logger.catch
@auth
async def bills(message: types.Message, data, **kwargs):
    vpn = data.get('vpn')
    bills_data = get_pending_bills_data_by_vpn(vpn.id)
    if bills_data:
        await message.answer(f'Вот ваши счета на оплату:', reply_markup=pending_bills(bills_data))
    else:
        await message.answer(f'У вас нету счетов на оплату')

@logger.catch
async def information(message:types.Message):
    await message.answer(f'Информация')

@logger.catch
@auth
async def instruction(message : types.Message, data, **kwargs):
    """ Выдает пользователю инструкцию из файла """
    with open('text/instruction.txt', 'r') as instruction:
        text = instruction.read()
    await message.answer(text)

@logger.catch
@auth
async def get_vpn_trial(message: types.Message, data, **kwargs):
    """ Создает trial vpn на 3 дня для тестирования пользователем """
    user = data.get('user')
    logger.info(f'Получен запрос на пробный VPN от пользователя {user.id}')
    await message.answer(f'Пробная версия выдается на 3 дня.\n'\
                            f'Статус твоего аккаунта можно посмотреть\n'\
                            f'по кнопке "МойПрофиль"')
    if user.status == 'created':
        result = create_vpn(user)
        if result:
            await message.answer('Получили Ваш запрос.\nОжидайте формирования настроек.\nОбычно занимает около 5 минут.',
            reply_markup=start_executed_user                                    )
        else:
            await message.answer('Что-то пошло не так, обратитесь в техническую поддержку @endurancevpnsupport')
    else:
        await message.answer('Для вас уже создан VPN', reply_markup=start_executed_user)

@logger.catch
@auth
async def buy_vpn(message: types.Message, data, **kwargs):
    await message.answer('Выберите тарифный план:', reply_markup=tariffs_keyboard())

@logger.catch
async def pay(callback: types.CallbackQuery, callback_data: dict):
    tariff = get_tariff(callback_data.get('id'))
    data = get_user_data(callback.from_user.id)
    vpn = data.get('vpn')
    bills_data = get_pending_bills_data_by_vpn(vpn.id)
    if len(bills_data) >= const.MAX_BIILS:
        await callback.message.edit_text(f'Вам выставлено максимальное количество счетов. Вы можете оплатить их в личном кабинете.')
    else:
        bill_id = create_bill(vpn, tariff)
        user = data.get('user')
        logger.info(f'Для пользователя {user.id} выставлен счет {bill_id}')
        await callback.message.edit_text(f'Ваш счет на сумму {tariff.price}р на {tariff.days} дней', reply_markup=pay_keyboard(bill_id))

@logger.catch
async def back_tariff(callback: types.CallbackQuery):
    await callback.message.edit_text('Выберите тарифный план:', reply_markup=tariffs_keyboard())

@logger.catch
async def cancel_buy(callback: types.CallbackQuery):
    await callback.message.delete()


def register_user_handlers(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(register, commands=['Регистрация'])
    dp.register_message_handler(register_set_name, state=RegistrationStates.name)
    dp.register_message_handler(buy_vpn, commands=['ПродлитьVPN'])
    dp.register_message_handler(get_vpn_trial, commands=['ПробнаяВерсия'])
    dp.register_message_handler(instruction, commands=['Инструкция'])
    dp.register_message_handler(information, commands=['Информация'])
    dp.register_message_handler(profile, commands=['МойПрофиль'])
    dp.register_message_handler(bills, commands=['МоиСчета'])
    dp.register_callback_query_handler(pay, tariffs_cd.filter(tariff='tariff'))
    dp.register_callback_query_handler(back_tariff, text='back_tariff')
    dp.register_callback_query_handler(cancel_buy, text='cancel_buy')