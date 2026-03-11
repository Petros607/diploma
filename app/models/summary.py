# app/models/summary.py
from sqlalchemy import Column, Integer, ForeignKey, Text, String
from sqlalchemy.orm import relationship

from app.database import Base


class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), unique=True)
    annotation = Column(Text)
    summary_path = Column(String)
    lecture = relationship("Lecture", back_populates="summary")
