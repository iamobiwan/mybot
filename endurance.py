from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import aioschedule
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers
from services.actions import check_pending_users, check_vpn_expire, rebuild_server_config, check_pending_bills
from loader import dp, logger
from datetime import datetime

# регистрируем хендлеры
register_admin_handlers(dp)
register_user_handlers(dp)

async def scheduler():
    aioschedule.every(15).seconds.do(check_pending_users)
    aioschedule.every(2).minutes.do(check_vpn_expire)
    aioschedule.every(3).minutes.do(rebuild_server_config)
    aioschedule.every(4).minutes.do(check_pending_bills)
    # aioschedule.every().day.at('00:01').do(check_vpn_expire)
    # aioschedule.every().day.at('00:02').do(rebuild_server_config)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
   
async def on_startup(_):
    logger.info(f'Бот запущен... Время: {datetime.now()}')
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)