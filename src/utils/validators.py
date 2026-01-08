"""Валидация данных заявок."""
import re


def validate_name(name: str) -> tuple[bool, str]:
    """
    Валидация имени пользователя.
    
    Returns:
        (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Имя не может быть пустым"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Имя должно содержать минимум 2 символа"
    
    if len(name) > 100:
        return False, "Имя слишком длинное (максимум 100 символов)"
    
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', name):
        return False, "Имя может содержать только буквы, пробелы и дефисы"
    
    return True, ""


def validate_contact(contact: str) -> tuple[bool, str]:
    """
    Валидация контакта (телефон или email).
    
    Returns:
        (is_valid, error_message)
    """
    if not contact or not contact.strip():
        return False, "Контакт не может быть пустым"
    
    contact = contact.strip()
    
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, contact):
        return True, ""
    
    phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    
    telegram_pattern = r'^@?[a-zA-Z0-9_]{5,32}$'
    
    if re.match(phone_pattern, contact) or re.match(telegram_pattern, contact):
        return True, ""
    
    return False, "Контакт должен быть email, телефоном или Telegram username"


def validate_task_description(description: str) -> tuple[bool, str]:
    """
    Валидация описания задачи.
    
    Returns:
        (is_valid, error_message)
    """
    if not description or not description.strip():
        return False, "Описание задачи не может быть пустым"
    
    description = description.strip()
    
    if len(description) < 10:
        return False, "Описание должно содержать минимум 10 символов"
    
    if len(description) > 2000:
        return False, "Описание слишком длинное (максимум 2000 символов)"
    
    return True, ""

