"""Точка входа приложения."""
import asyncio
import signal
import sys
from src.config import Config
from src.database.db import init_db
from src.parser.channel_parser import ChannelParser
from src.bot.bot import start_bot, stop_bot, create_bot


parser = None
bot = None
dp = None


async def main():
    """Основная функция запуска приложения."""
    global parser, bot, dp
    
    try:
        Config.validate()
        print("✅ Конфигурация загружена успешно")
        
        init_db()
        print("✅ База данных инициализирована")
        
        parser = ChannelParser()
        parser_task = asyncio.create_task(parser.run_forever())
        print("✅ Парсер запущен")
        
        bot, dp = create_bot()
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Бот запущен")
        
        await asyncio.gather(
            dp.start_polling(bot),
            parser_task
        )
        
    except KeyboardInterrupt:
        print("\n⚠️ Получен сигнал остановки...")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await shutdown()


async def shutdown():
    """Корректное завершение работы приложения."""
    global parser, bot
    
    print("Завершение работы...")
    
    if parser:
        try:
            await parser.stop()
        except Exception as e:
            print(f"Ошибка при остановке парсера: {e}")
    
    if bot:
        try:
            await bot.session.close()
        except Exception as e:
            print(f"Ошибка при остановке бота: {e}")
    
    print("✅ Приложение остановлено")


def signal_handler(sig, frame):
    """Обработчик сигналов для graceful shutdown."""
    print("\n⚠️ Получен сигнал остановки...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Приложение завершено")

