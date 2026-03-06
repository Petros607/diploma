from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)

    annotation = Column(Text)
    summary_path = Column(String)
