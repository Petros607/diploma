# app/schemas/lecture.py
from pydantic import BaseModel
from datetime import datetime


class LectureBase(BaseModel):
    title: str


class LectureCreate(LectureBase):
    pass


class LectureResponse(LectureBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
