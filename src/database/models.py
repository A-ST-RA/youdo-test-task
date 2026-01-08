"""Модели базы данных."""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from src.database.db import Base


class ApplicationStatus(enum.Enum):
    """Статусы заявки."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Post(Base):
    """Модель для спарсенных постов из Telegram-канала."""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, nullable=False, index=True)
    message_id = Column(Integer, nullable=False, unique=True, index=True)
    service_type = Column(String, nullable=True)  
    description = Column(String, nullable=True)  
    published_date = Column(DateTime, nullable=True)  
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Post(id={self.id}, message_id={self.message_id}, service_type={self.service_type})>"


class Application(Base):
    """Модель для заявок от пользователей."""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_name = Column(String, nullable=False)
    contact = Column(String, nullable=False)  
    task_description = Column(String, nullable=False)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.NEW, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Application(id={self.id}, user_id={self.user_id}, status={self.status.value})>"

