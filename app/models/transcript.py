from sqlalchemy import Column, Integer, String
from app.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True)

    audio_file = Column(String)
    transcript_path = Column(String)
