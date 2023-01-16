from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from states import RegistrationStates
from db.queries.users import create_user, get_user

async def admin_start(message : types.Message):
    if message.from_user.id in message.bot.get('config').tg_bot.admin_ids:
        print('Вы админ')

def register_admin_handlers(dp : Dispatcher):
    dp.register_message_handler(admin_start, commands=['iamobiwan'])