"""Инициализация базы данных."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import Config


Base = declarative_base()


engine = create_engine(
    Config.DATABASE_URL,
    connect_args={'check_same_thread': False} if 'sqlite' in Config.DATABASE_URL else {}
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Инициализация базы данных - создание всех таблиц."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Получение сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

