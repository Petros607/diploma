# app/models/lecture.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    teacher = Column(String)
    subject = Column(String)

    url = Column(String, unique=True)

    datetime = Column(String)

    transcript = relationship(
        "Transcript",
        back_populates="lecture",
        uselist=False,
        cascade="all, delete"
    )

    summary = relationship(
        "Summary",
        back_populates="lecture",
        uselist=False,
        cascade="all, delete"
    )

    presentation = relationship(
        "Presentation",
        back_populates="lecture",
        uselist=False,
        cascade="all, delete"
    )

    requests = relationship(
        "Request",
        back_populates="lecture",
        cascade="all, delete"
    )
