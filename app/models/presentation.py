from sqlalchemy import Column, Integer, String, JSON
from app.database import Base


class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(Integer, primary_key=True)

    slide_timings = Column(JSON)
    presentation_path = Column(String)
