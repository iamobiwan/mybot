from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from states import RegistrationStates
from db.queries import create_user, get_user
from keyboards.reply import start_new_user, start_created_user, start_executed_user
from services.vpn import generate_user_config, create_vpn, choose_server


async def start(message : types.Message):
    """ Старт бота, проверка регистрации пользователя """
    user = get_user(message.from_user.id)
    if user:
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
    user = get_user(message.from_user.id)
    if user:
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
    
async def instruction(message : types.Message):
    with open('text/instruction.txt', 'r') as instruction:
        text = instruction.read()
    await message.answer(text)

async def get_vpn(message: types.Message):
    user = get_user(message.from_user.id)
    user_id = user.id
    if user:
        server = choose_server()
        if server:
            if user.status == 'created':
                result = create_vpn(user, server)
                if result:
                    await message.answer('Вот ваш QR код')
                    with open(f'users/qr/{user_id}.png', 'rb') as photo:
                        await message.bot.send_photo(message.chat.id, photo, reply_markup=start_executed_user)
                else:
                    await message.answer('Что-то пошло не так')
            else:
                await message.answer('Для вас уже создан VPN', reply_markup=start_executed_user)
        else:
            await message.answer('Нет свободных серверов', reply_markup=start_created_user)
    else:
        await message.answer('Вы не зарегистрированы', reply_markup=start_new_user)
    
def register_user_handlers(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(register, commands=['Регистрация'])
    dp.register_message_handler(register_set_name, state=RegistrationStates.name)
    dp.register_message_handler(get_vpn, commands=['ПолучитьVPN'])
    dp.register_message_handler(instruction, commands=['Инструкция'])