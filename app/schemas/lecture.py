# app/schemas/lecture.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LectureBase(BaseModel):
    title: str

class LectureCreate(BaseModel):
    url: str


class LectureResponse(BaseModel):
    id: int
    url: str
    subject: str | None
    teacher: str | None
    datetime: str | None

    model_config = ConfigDict(from_attributes=True)
