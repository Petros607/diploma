from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LectureBase(BaseModel):
    title: str

class LectureCreate(LectureBase):
    pass

class LectureResponse(LectureBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
