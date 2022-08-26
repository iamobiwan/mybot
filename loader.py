from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import load_config

config = load_config()      # конфиг из переменных окружения

storage = MemoryStorage() 

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=storage)

bot['config'] = config  # потом, чтобы получить доступ к конфигу bot.get('config')