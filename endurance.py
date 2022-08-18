from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import load_config
from handlers import register_handler_echo

storage = MemoryStorage()

def register_all_handlers(dp : Dispatcher):
    register_handler_echo(dp)


config = load_config()

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=storage)

# чтобы из хендлеров был доступ к конфигу
bot['config'] = config
# потом, чтобы получить доступ к конфигу bot.get('config')

# регистрируем хендлеры
register_all_handlers(dp)

async def on_startup(_):
    print('Бот запущен...')    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)