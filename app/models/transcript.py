# app/models/transcript.py
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), unique=True)
    audio_path = Column(String)
    transcript_path = Column(String)
    lecture = relationship("Lecture", back_populates="transcript")
