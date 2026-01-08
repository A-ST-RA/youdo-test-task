"""Клавиатуры для Telegram-бота."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from src.database.models import ApplicationStatus


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота."""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📋 Создать заявку"))
    builder.add(KeyboardButton(text="📰 Просмотреть посты"))
    builder.add(KeyboardButton(text="📊 Статистика заявок"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены."""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)


def get_posts_keyboard(page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Клавиатура для навигации по постам."""
    builder = InlineKeyboardBuilder()
    
    if total_pages > 1:
        if page > 0:
            builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data=f"posts_page_{page-1}"))
        if page < total_pages - 1:
            builder.add(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"posts_page_{page+1}"))
        builder.adjust(2)
    
    builder.add(InlineKeyboardButton(text="🔄 Обновить", callback_data="posts_refresh"))
    
    return builder.as_markup()


def get_application_status_keyboard(application_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для изменения статуса заявки (для админов)."""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="🆕 Новая",
        callback_data=f"app_status_{application_id}_new"
    ))
    builder.add(InlineKeyboardButton(
        text="⚙️ В работе",
        callback_data=f"app_status_{application_id}_in_progress"
    ))
    builder.add(InlineKeyboardButton(
        text="✅ Завершена",
        callback_data=f"app_status_{application_id}_completed"
    ))
    builder.adjust(1)
    
    return builder.as_markup()

