# app/schemas/lecture.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LectureBase(BaseModel):
    title: str

class LectureCreate(BaseModel):
    url: str
    subject: str | None = ""
    teacher: str | None = ""
    datetime: str | None = ""


class LectureResponse(BaseModel):
    id: int
    url: str
    subject: str | None
    teacher: str | None
    datetime: str | None

    model_config = ConfigDict(from_attributes=True)


# additional schemas for API communication
from typing import Dict, Optional
from app.core.status import RequestStatus


class LectureGenerateResponse(BaseModel):
    status: RequestStatus
    lecture_id: int
    request_id: int


class LectureStatusResponse(BaseModel):
    status: RequestStatus
    lecture_id: Optional[int] = None
    request_id: Optional[int] = None


class RoomLecture(BaseModel):
    name_teacher: str
    name_subject: str
    datetime: str
    url: str
    length: str
    users_count: int
    status: RequestStatus


from pydantic import RootModel


class RoomLecturesResponse(RootModel[RoomLecture]):
    root: Dict[str, RoomLecture]

