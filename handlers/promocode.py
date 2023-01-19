from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from db.models import User
from states.promocode import PromocodeStates
from db.queries.common import update_item
from db.queries.users import create_user
from db.connect import session_maker
from keyboards.inline import back_main
from services.decorators import auth
from loader import logger
from datetime import datetime
import const
import string
import random



@logger.catch
@auth
async def get_promocode(callback: types.CallbackQuery, user, **kwargs):
    if not user.promocode:
        promocode = ''.join(random.choice(string.ascii_uppercase) for i in range(const.LEN_PROMOCODE))
        user.promocode = promocode
    await callback.message.edit_text(
            f'Ваш промокод:\n\n'\
            f'`{user.promocode}`\n\n'\
            f'Поделитесь им с друзьями, чтобы получить скидку 100₽ на следующее продление за каждого друга!',
            parse_mode='Markdown',
            reply_markup=back_main()
            )
    update_item(user)

@logger.catch
async def apply_promocode(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'Введите промокод')
    await PromocodeStates.promocode.set()

@logger.catch
@auth
async def promocode_check(message : types.Message, user, state: FSMContext, **kwargs):
    with session_maker() as session:
        promocode = message.text
        user_who_invite = session.query(User).filter(User.promocode == promocode).first()
        if user_who_invite:
            if not user:
                user = create_user(message.from_user.id, message.from_user.full_name)
            if user.promocode_used:
                await message.answer(
                f'Вы уже применили промокод!',
                reply_markup=back_main()
                )
                await state.finish()
                return
            logger.info('Функция продолжилась')
            user.discount += const.DISCOUNT_FOR_NEW_USER
            user.invite_from_user_id = user_who_invite.id
            user.invite_discount = True
            user.updated_at = datetime.now()
            user.promocode_used = True
            await message.answer(
                f'Промокод применен!\n\n'\
                f'Ваша скидка будет применена при следующем продлении подписки.',
                parse_mode='Markdown',
                reply_markup=back_main()
                )
            session.add(user)
            session.commit()
        else:
            await message.answer(
                f'Такого промокода не существует!',
                parse_mode='Markdown',
                reply_markup=back_main()
                )
        await state.finish()


def register_promocode_handlers(dp : Dispatcher):
    dp.register_callback_query_handler(get_promocode, text='get_promocode')
    dp.register_callback_query_handler(apply_promocode, text='apply_promocode')
    dp.register_message_handler(promocode_check, state=PromocodeStates.promocode)