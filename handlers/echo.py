from aiogram import Dispatcher, types

async def bot_echo(message: types.Message):
    text = [
        'Эхо сообщение',
        message.text
    ]
    await message.answer('\n'.join(text))

def register_handler_echo(dp : Dispatcher):
    dp.register_message_handler(bot_echo)