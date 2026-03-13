# app/schemas/request.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class RequestBase(BaseModel):
    lecture_id: int
    status: str

class RequestCreate(RequestBase):
    pass

class RequestResponse(BaseModel):
    id: int
    lecture_id: int
    status: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
