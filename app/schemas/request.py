from pydantic import BaseModel, ConfigDict
from datetime import datetime

class RequestBase(BaseModel):
    lecture_id: int
    status: str

class RequestCreate(RequestBase):
    pass

class RequestResponse(RequestBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
