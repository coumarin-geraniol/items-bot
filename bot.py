import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging
from config_reader import config
from database.database import db_start
from handlers import auth, catalog, fsm, cart, type_cargo, register
from global_vars import set_available_items_title
from handlers.main import get_available_items_title_db


async def start_bot(bot: Bot):
    await db_start()
    set_available_items_title(await get_available_items_title_db())
    await bot.send_message(config.admin_id.get_secret_value(), text='Bot started')
    print('Bot started')


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=config.bot_token.get_secret_value())

    await bot.delete_webhook(drop_pending_updates=True)

    dp.startup.register(start_bot)
    dp.include_router(auth.router)
    dp.include_router(register.router)
    dp.include_router(type_cargo.router)
    dp.include_router(fsm.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
