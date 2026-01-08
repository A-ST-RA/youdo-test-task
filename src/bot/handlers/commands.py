"""Обработчики команд бота."""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from src.bot.keyboards import get_main_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    welcome_text = (
        "👋 Добро пожаловать!\n\n"
        "Я бот для обработки заявок и просмотра новостей команды.\n\n"
        "Доступные функции:\n"
        "• 📋 Создание заявок\n"
        "• 📰 Просмотр постов из канала команды\n"
        "• 📊 Статистика заявок\n\n"
        "Используйте кнопки ниже или команду /help для получения справки."
    )
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    help_text = (
        "📖 Справка по использованию бота\n\n"
        "Команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/posts - Просмотреть посты из канала\n"
        "/stats - Статистика заявок\n\n"
        "Действия:\n"
        "• Нажмите '📋 Создать заявку' для подачи новой заявки\n"
        "• Нажмите '📰 Просмотреть посты' для просмотра новостей команды\n"
        "• Нажмите '📊 Статистика заявок' для просмотра статистики\n\n"
        "При создании заявки вам нужно будет указать:\n"
        "• Ваше имя\n"
        "• Контакт (email, телефон или Telegram username)\n"
        "• Описание задачи"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard())


@router.message(Command("posts"))
async def cmd_posts(message: Message):
    """Обработчик команды /posts - перенаправляет на обработчик постов."""
    from src.bot.handlers.posts import show_posts
    await show_posts(message)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats - перенаправляет на обработчик статистики."""
    from src.bot.handlers.applications import show_statistics
    await show_statistics(message)


@router.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message):
    """Обработчик кнопки помощи."""
    await cmd_help(message)

