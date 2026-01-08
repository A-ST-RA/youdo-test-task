"""Обработчики для отображения постов из канала."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.database.db import SessionLocal
from src.database.models import Post
from src.bot.keyboards import get_posts_keyboard
from datetime import datetime

router = Router()

POSTS_PER_PAGE = 5


def format_post(post: Post) -> str:
    """Форматирование поста для отображения."""
    text = f"📰 Пост #{post.message_id}\n\n"
    
    if post.service_type:
        text += f"🏷 Тип услуги/проекта: {post.service_type}\n"
    
    if post.description:
        description = post.description[:300] + "..." if len(post.description) > 300 else post.description
        text += f"\n📝 Описание:\n{description}\n"
    
    if post.published_date:
        date_str = post.published_date.strftime("%d.%m.%Y %H:%M")
        text += f"\n📅 Дата публикации: {date_str}\n"
    
    text += f"\n🕐 Обработано: {post.created_at.strftime('%d.%m.%Y %H:%M')}"
    
    return text


@router.message(F.text == "📰 Просмотреть посты")
async def show_posts(message: Message, page: int = 0):
    """Отображение списка постов."""
    db = SessionLocal()
    try:
        total_posts = db.query(Post).count()
        
        if total_posts == 0:
            await message.answer(
                "📭 Пока нет сохраненных постов из канала.\n"
                "Посты будут появляться здесь автоматически после публикации в канале."
            )
            return
        
        total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
        
        posts = db.query(Post).order_by(desc(Post.created_at)).offset(
            page * POSTS_PER_PAGE
        ).limit(POSTS_PER_PAGE).all()
        
        if not posts:
            await message.answer("Постов на этой странице нет.")
            return
        
        response_text = f"📰 Посты из канала команды\n\n"
        response_text += f"Страница {page + 1} из {total_pages}\n"
        response_text += f"Всего постов: {total_posts}\n\n"
        response_text += "─" * 30 + "\n\n"
        
        for post in posts:
            response_text += format_post(post) + "\n\n"
            response_text += "─" * 30 + "\n\n"
        
        await message.answer(
            response_text,
            reply_markup=get_posts_keyboard(page, total_pages)
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении постов: {e}")
    finally:
        db.close()


@router.callback_query(F.data.startswith("posts_page_"))
async def posts_pagination(callback: CallbackQuery):
    """Обработка пагинации постов."""
    try:
        page = int(callback.data.split("_")[-1])
        await callback.answer()
        if callback.message:
            await show_posts(callback.message, page=page)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)


@router.callback_query(F.data == "posts_refresh")
async def posts_refresh(callback: CallbackQuery):
    """Обновление списка постов."""
    await callback.answer("Обновление...")
    if callback.message:
        await show_posts(callback.message, page=0)

