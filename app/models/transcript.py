# app/models/transcript.py
from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True)

    lecture_id = Column(Integer, ForeignKey("lectures.id"), unique=True)

    text = Column(Text)

    lecture = relationship("Lecture", back_populates="transcript")
