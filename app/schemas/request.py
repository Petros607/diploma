# app/schemas/request.py
from pydantic import BaseModel
from datetime import datetime


class RequestBase(BaseModel):
    lecture_id: int
    status: str


class RequestCreate(RequestBase):
    pass


class RequestResponse(RequestBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
