"""Конфигурация приложения с загрузкой переменных окружения."""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Класс для хранения конфигурации приложения."""
    
    API_ID: int = int(os.getenv('API_ID', '0'))
    API_HASH: str = os.getenv('API_HASH', '')
    
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    CHANNEL_ID: str = os.getenv('CHANNEL_ID', '')
    
    MANAGER_ID: int = int(os.getenv('MANAGER_ID', '0'))
    LEADER_ID: int = int(os.getenv('LEADER_ID', '0'))
    
    SESSION_NAME: str = os.getenv('SESSION_NAME', 'telegram_session')
    
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./telegram_bot.db')
    
    @classmethod
    def validate(cls) -> bool:
        """Проверка наличия всех необходимых переменных окружения."""
        required_vars = {
            'API_ID': cls.API_ID,
            'API_HASH': cls.API_HASH,
            'BOT_TOKEN': cls.BOT_TOKEN,
            'CHANNEL_ID': cls.CHANNEL_ID,
            'MANAGER_ID': cls.MANAGER_ID,
            'LEADER_ID': cls.LEADER_ID,
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        
        if missing:
            raise ValueError(
                f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}"
            )
        
        return True

