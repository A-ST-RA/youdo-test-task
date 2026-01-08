"""Парсер Telegram-канала для извлечения информации из постов."""
import asyncio
import re
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Message
from sqlalchemy.orm import Session
from src.config import Config
from src.database.models import Post
from src.database.db import SessionLocal


class ChannelParser:
    """Класс для парсинга Telegram-канала."""
    
    def __init__(self):
        self.client = TelegramClient(
            Config.SESSION_NAME,
            Config.API_ID,
            Config.API_HASH
        )
        
        try:
            self.channel_id = int(Config.CHANNEL_ID)
        except (ValueError, TypeError):
            self.channel_id = Config.CHANNEL_ID
        self.running = False
    
    async def start(self):
        """Запуск парсера."""
        await self.client.start()
        self.running = True
        
        @self.client.on(events.NewMessage(chats=self.channel_id))
        async def handler(event: events.NewMessage.Event):
            await self._process_message(event.message)
        
        print(f"Парсер запущен и отслеживает канал: {self.channel_id}")
    
    async def _process_message(self, message: Message):
        """Обработка нового сообщения из канала."""
        try:
            db = SessionLocal()
            try:
                existing_post = db.query(Post).filter(
                    Post.message_id == message.id
                ).first()
                
                if existing_post:
                    return
                
                parsed_data = self._parse_message(message.text or "")
                
                post = Post(
                    channel_id=str(self.channel_id),
                    message_id=message.id,
                    service_type=parsed_data.get('service_type'),
                    description=parsed_data.get('description'),
                    published_date=message.date if message.date else datetime.now()
                )
                
                db.add(post)
                db.commit()
                
                print(f"Обработано новое сообщение: ID={message.id}, Тип услуги={parsed_data.get('service_type')}")
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"Ошибка при обработке сообщения: {e}")
    
    def _parse_message(self, text: str) -> dict:
        """Парсинг текста сообщения для извлечения информации."""
        result = {
            'service_type': None,
            'description': None
        }
        
        if not text:
            return result
        
        service_patterns = [
            r'(?:тип|услуга|проект|вид)[\s:]+([^\n]+)',
            r'(?:выполнен|сделан|реализован)[\s:]+([^\n]+)',
        ]
        
        for pattern in service_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['service_type'] = match.group(1).strip()
                break
        
        if not result['service_type']:
            lines = text.split('\n')
            if lines:
                first_line = lines[0].strip()
                if len(first_line) < 100:
                    result['service_type'] = first_line
        
        result['description'] = text[:500] if len(text) > 500 else text
        
        return result
    
    async def stop(self):
        """Остановка парсера."""
        self.running = False
        await self.client.disconnect()
        print("Парсер остановлен")
    
    async def run_forever(self):
        """Запуск парсера в бесконечном цикле."""
        await self.start()
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            await self.stop()

