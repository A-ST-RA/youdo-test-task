"""Обработчики заявок."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from src.database.db import SessionLocal
from src.database.models import Application, ApplicationStatus
from src.bot.keyboards import get_main_keyboard, get_cancel_keyboard, get_application_status_keyboard
from src.utils.validators import validate_name, validate_contact, validate_task_description
from src.config import Config
from aiogram import Bot

router = Router()


class ApplicationForm(StatesGroup):
    """Состояния FSM для создания заявки."""
    name = State()
    contact = State()
    task_description = State()


@router.message(F.text == "📋 Создать заявку")
async def start_application(message: Message, state: FSMContext):
    """Начало создания заявки."""
    await state.set_state(ApplicationForm.name)
    await message.answer(
        "📋 Создание новой заявки\n\n"
        "Пожалуйста, введите ваше имя:",
        reply_markup=get_cancel_keyboard()
    )


@router.message(F.text == "❌ Отмена")
async def cancel_application(message: Message, state: FSMContext):
    """Отмена создания заявки."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активной заявки для отмены.")
        return
    
    await state.clear()
    await message.answer(
        "❌ Создание заявки отменено.",
        reply_markup=get_main_keyboard()
    )


@router.message(ApplicationForm.name)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени."""
    name = message.text
    
    is_valid, error = validate_name(name)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПожалуйста, введите имя еще раз:")
        return
    
    await state.update_data(name=name)
    await state.set_state(ApplicationForm.contact)
    await message.answer(
        f"✅ Имя сохранено: {name}\n\n"
        "Теперь введите контакт для связи:\n"
        "(email, телефон или Telegram username)"
    )


@router.message(ApplicationForm.contact)
async def process_contact(message: Message, state: FSMContext):
    """Обработка контакта."""
    contact = message.text
    
    is_valid, error = validate_contact(contact)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПожалуйста, введите контакт еще раз:")
        return
    
    await state.update_data(contact=contact)
    await state.set_state(ApplicationForm.task_description)
    await message.answer(
        f"✅ Контакт сохранен: {contact}\n\n"
        "Теперь опишите задачу (минимум 10 символов):"
    )


@router.message(ApplicationForm.task_description)
async def process_task_description(message: Message, state: FSMContext, bot: Bot):
    """Обработка описания задачи и сохранение заявки."""
    description = message.text
    
    is_valid, error = validate_task_description(description)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПожалуйста, опишите задачу еще раз:")
        return
    
    data = await state.get_data()
    
    db = SessionLocal()
    try:
        application = Application(
            user_id=message.from_user.id,
            user_name=data['name'],
            contact=data['contact'],
            task_description=description,
            status=ApplicationStatus.NEW
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        
        notification_text = (
            f"🔔 Новая заявка #{application.id}\n\n"
            f"👤 Имя: {application.user_name}\n"
            f"📞 Контакт: {application.contact}\n"
            f"📝 Описание задачи:\n{application.task_description}\n\n"
            f"📅 Создана: {application.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"🆔 ID пользователя: {application.user_id}\n"
            f"📊 Статус: Новая"
        )
        
        try:
            if Config.LEADER_ID:
                await bot.send_message(Config.LEADER_ID, notification_text)
            if Config.MANAGER_ID:
                await bot.send_message(Config.MANAGER_ID, notification_text)
        except Exception as e:
            print(f"Ошибка при отправке уведомлений: {e}")
        
        await message.answer(
            "✅ Заявка успешно создана и отправлена руководителю и менеджеру!\n\n"
            f"Номер заявки: #{application.id}\n"
            "Мы свяжемся с вами в ближайшее время.",
            reply_markup=get_main_keyboard()
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при сохранении заявки: {e}",
            reply_markup=get_main_keyboard()
        )
    finally:
        db.close()
        await state.clear()


@router.message(F.text == "📊 Статистика заявок")
async def show_statistics(message: Message):
    """Отображение статистики заявок."""
    db = SessionLocal()
    try:
        user_id = message.from_user.id
        
        is_admin = (user_id == Config.LEADER_ID or user_id == Config.MANAGER_ID)
        
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if is_admin:
            total = db.query(Application).count()
            today = db.query(Application).filter(Application.created_at >= today_start).count()
            week = db.query(Application).filter(Application.created_at >= week_start).count()
            month = db.query(Application).filter(Application.created_at >= month_start).count()
            
            new_count = db.query(Application).filter(Application.status == ApplicationStatus.NEW).count()
            in_progress_count = db.query(Application).filter(Application.status == ApplicationStatus.IN_PROGRESS).count()
            completed_count = db.query(Application).filter(Application.status == ApplicationStatus.COMPLETED).count()
            
            stats_text = (
                f"📊 Статистика заявок\n\n"
                f"📈 Всего заявок: {total}\n\n"
                f"📅 За сегодня: {today}\n"
                f"📅 За неделю: {week}\n"
                f"📅 За месяц: {month}\n\n"
                f"📋 По статусам:\n"
                f"🆕 Новые: {new_count}\n"
                f"⚙️ В работе: {in_progress_count}\n"
                f"✅ Завершены: {completed_count}"
            )
        else:
            user_total = db.query(Application).filter(Application.user_id == user_id).count()
            user_today = db.query(Application).filter(
                Application.user_id == user_id,
                Application.created_at >= today_start
            ).count()
            user_week = db.query(Application).filter(
                Application.user_id == user_id,
                Application.created_at >= week_start
            ).count()
            user_month = db.query(Application).filter(
                Application.user_id == user_id,
                Application.created_at >= month_start
            ).count()
            
            stats_text = (
                f"📊 Ваша статистика заявок\n\n"
                f"📈 Всего ваших заявок: {user_total}\n\n"
                f"📅 За сегодня: {user_today}\n"
                f"📅 За неделю: {user_week}\n"
                f"📅 За месяц: {user_month}"
            )
        
        await message.answer(stats_text, reply_markup=get_main_keyboard())
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статистики: {e}")
    finally:
        db.close()


@router.callback_query(F.data.startswith("app_status_"))
async def change_application_status(callback: CallbackQuery, bot: Bot):
    """Изменение статуса заявки (только для админов)."""
    try:
        user_id = callback.from_user.id
        is_admin = (user_id == Config.LEADER_ID or user_id == Config.MANAGER_ID)
        
        if not is_admin:
            await callback.answer("❌ У вас нет прав для изменения статуса заявок", show_alert=True)
            return
        
        parts = callback.data.split("_")
        application_id = int(parts[2])
        new_status_str = parts[3]
        
        status_map = {
            'new': ApplicationStatus.NEW,
            'in_progress': ApplicationStatus.IN_PROGRESS,
            'completed': ApplicationStatus.COMPLETED
        }
        
        new_status = status_map.get(new_status_str)
        if not new_status:
            await callback.answer("❌ Неверный статус", show_alert=True)
            return
        
        db = SessionLocal()
        try:
            application = db.query(Application).filter(Application.id == application_id).first()
            if not application:
                await callback.answer("❌ Заявка не найдена", show_alert=True)
                return
            
            old_status = application.status
            application.status = new_status
            db.commit()
            
            status_names = {
                ApplicationStatus.NEW: "Новая",
                ApplicationStatus.IN_PROGRESS: "В работе",
                ApplicationStatus.COMPLETED: "Завершена"
            }
            
            await callback.answer(
                f"✅ Статус заявки #{application_id} изменен на: {status_names[new_status]}",
                show_alert=True
            )
            
            try:
                notification = (
                    f"📢 Обновление статуса заявки #{application_id}\n\n"
                    f"Статус изменен: {status_names[old_status]} → {status_names[new_status]}"
                )
                await bot.send_message(application.user_id, notification)
            except Exception as e:
                print(f"Ошибка при отправке уведомления пользователю: {e}")
                
        finally:
            db.close()
            
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)

