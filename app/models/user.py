# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean
# Импортируем Base из нашего файла настроек БД (который мы исправили ранее)
from app.database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    # ВАЖНО: В базе мы храним хэш пароля, а не сам пароль!
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
