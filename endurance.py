from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers
from config import load_config

storage = MemoryStorage()   # сторадж для состояний
config = load_config()      # конфиг из переменных окружения

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=storage)

bot['config'] = config  # потом, чтобы получить доступ к конфигу bot.get('config')

# регистрируем хендлеры
register_admin_handlers(dp)
register_user_handlers(dp)

async def on_startup(_):
    print('Бот запущен...')    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)