# app/models/presentation.py
from sqlalchemy import Column, Integer, ForeignKey, String, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Presentation(Base):
    __tablename__ = "presentations"
    id = Column(Integer, primary_key=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), unique=True)
    slides_timings = Column(JSON)
    presentation_path = Column(String)
    lecture = relationship("Lecture", back_populates="presentation")
