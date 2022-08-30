from aiogram import types
from db.queries import user_exists, get_user_data
from keyboards.reply import start_new_user

def auth(func):
    async def inner(message: types.Message, **kwargs):
        data = get_user_data(message.from_user.id)
        if data:
            await func(message, data, **kwargs)
        else:
            await message.answer('Вы не зарегистрированы', reply_markup=start_new_user)
    return inner