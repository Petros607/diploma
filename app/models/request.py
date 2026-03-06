# app/models/request.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)

    lecture_id = Column(Integer, ForeignKey("lectures.id"), unique=True)

    status = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    lecture = relationship("Lecture", back_populates="requests")
