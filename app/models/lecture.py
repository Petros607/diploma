from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    lecturer = Column(String, nullable=False)
    lecture_date = Column(Date)

    video_url = Column(String, unique=True, index=True)

    summary_id = Column(Integer)
    transcript_id = Column(Integer)
    presentation_id = Column(Integer)

    requests = relationship("Request", back_populates="lecture")
