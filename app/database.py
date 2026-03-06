# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Важно: используем префикс sqlite+aiosqlite для асинхронной работы
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

# 1. Создаем асинхронный движок (Async Engine)
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Нужно только для SQLite
)

# 2. Создаем фабрику асинхронных сессий.
# expire_on_commit=False — важная настройка для async, чтобы объекты не "протухали" после комита.
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Базовый класс для моделей (современный синтаксис SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

# 4. Dependency (Зависимость).
# Это асинхронный генератор.
async def get_db():
    # Используем async with — это гарантирует, что сессия закроется корректно
    async with AsyncSessionLocal() as db:
        yield db
