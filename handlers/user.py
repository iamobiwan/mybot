from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from states import RegistrationStates
from db.queries import create_user

async def register(message : types.Message):
    await message.answer('Укажите имя', reply_markup=ReplyKeyboardRemove())
    await RegistrationStates.name.set()

async def register_set_name(message : types.Message, state: FSMContext):
    name = message.text
    if len(name) > 15:  # Проверка на длину имени
        await message.answer(f'Имя слишком длинное, попробуй еще.')
        await RegistrationStates.name.set()
    elif "/" in name or "@" in name:
        await message.answer(f'Имя содержит не допустимые символы, попробуй еще.')
        await RegistrationStates.name.set()
    else:
        create_user(message.from_user.id, name)
        await message.answer(f'Регистрация завершена, {name}!')
        await state.finish()

def register_user_handlers(dp : Dispatcher):
    dp.register_message_handler(register, commands=['Регистрация'])
    dp.register_message_handler(register_set_name, state=RegistrationStates.name)