from aiogram import types
from db.queries import user_exists, get_user_data
from keyboards.reply import start_new_user
from loader import logger

def auth(func):
    async def inner(message: types.Message, **kwargs):
        data = get_user_data(message.from_user.id)
        if data:
            await func(message, data, **kwargs)
        else:
            logger.warning(f'Попытка не авторизованного доступа от пользователя с ID {message.from_user.id} команда: {message.get_command()}')
            await message.answer('Вы не зарегистрированы', reply_markup=start_new_user)
    return inner