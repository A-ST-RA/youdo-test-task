"""Инициализация и настройка Telegram-бота."""
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from src.config import Config
from src.bot.handlers import commands, applications, posts


def create_bot() -> tuple[Bot, Dispatcher]:
    """Создание экземпляра бота и диспетчера."""
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(commands.router)
    dp.include_router(applications.router)
    dp.include_router(posts.router)
    
    return bot, dp


async def start_bot():
    """Запуск бота."""
    bot, dp = create_bot()
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Бот запущен и готов к работе!")
    
    await dp.start_polling(bot)


async def stop_bot(bot: Bot):
    """Остановка бота."""
    await bot.session.close()
    print("Бот остановлен")

