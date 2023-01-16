from aiogram.utils import executor
import asyncio
import aioschedule
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers
from handlers.donate import register_donate_handlers
from handlers.vpn import register_vpn_handlers
from services.actions import check_pending_users, check_sub_expire, rebuild_server_config, check_pending_orders
from loader import dp, logger


# регистрируем хендлеры
register_admin_handlers(dp)
register_user_handlers(dp)
register_donate_handlers(dp)
register_vpn_handlers(dp)

# регулярные задания
async def scheduler():
    aioschedule.every(30).seconds.do(check_pending_users)
    aioschedule.every(45).seconds.do(check_sub_expire)
    aioschedule.every(60).seconds.do(check_pending_orders)
    aioschedule.every(120).seconds.do(rebuild_server_config)
    # aioschedule.every(5).minutes.do(check_pending_users)
    # aioschedule.every(8).minutes.do(check_pending_bills)
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