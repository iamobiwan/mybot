from aiogram import types
from db.queries.users import user_exists, get_user
from keyboards.reply import new_user
from loader import logger

def auth(func):
    async def inner(message: types.Message, **kwargs):
        user = get_user(message.from_user.id)
        await func(message, user, **kwargs)
            # logger.info('Пользователь не зарегистрирован')
            # logger.warning(f'Попытка не авторизованного доступа от пользователя с ID {callback.from_user.id} команда: {callback.get_command()}')
            # await callback.answer('Вы не зарегистрированы', reply_markup=new_user)
    return inner