from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import aioschedule
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers
from services.actions import check_pending_users, check_vpn_expire, rebuild_server_config, check_pending_bills, check_config, sync_config
from loader import dp, logger
from datetime import datetime

# регистрируем хендлеры
register_admin_handlers(dp)
register_user_handlers(dp)

async def scheduler():
    # aioschedule.every(30).seconds.do(check_pending_users)
    # aioschedule.every(45).seconds.do(check_pending_bills)
    # aioschedule.every(30).seconds.do(check_config)
    # aioschedule.every(75).seconds.do(check_vpn_expire)
    aioschedule.every(15).seconds.do(rebuild_server_config)
    # aioschedule.every(5).minutes.do(check_pending_users)
    # aioschedule.every(8).minutes.do(check_pending_bills)
    # aioschedule.every(10).minutes.do(check_config)
    # aioschedule.every().day.at('01:00').do(check_vpn_expire)
    # aioschedule.every().day.at('01:01').do(rebuild_server_config)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
   
async def on_startup(_):
    logger.info(f'Бот запущен...')
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)