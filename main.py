import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from bot.handlers import router, set_commands
from database.db import init_db

load_dotenv('.env.local')
BOT_TOKEN = os.getenv('BOT_TOKEN')
# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем роутер с хендлерами
dp.include_router(router)



async def main():
    # Инициализируем базу данных
    logging.info("Инициализация базы данных...")
    await init_db()
    logging.info("База данных инициализирована")

    # Регистрируем команды бота
    await set_commands(bot)

    # Удаляем все обновления, накопленные за время неактивности бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем бота
    logging.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
