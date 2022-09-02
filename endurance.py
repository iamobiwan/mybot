from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import aioschedule
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers
from config import load_config
from services.actions import check_vpn_expire, rebuild_server_config, check_pending_users
from loader import dp

# регистрируем хендлеры
register_admin_handlers(dp)
register_user_handlers(dp)

async def scheduler():
    aioschedule.every(1).minutes.do(check_vpn_expire)
    aioschedule.every(2).minutes.do(check_pending_users)
    aioschedule.every(3).minutes.do(rebuild_server_config)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
   
async def on_startup(_):
    print('Бот запущен...')
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)