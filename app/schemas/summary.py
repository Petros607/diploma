# app/schemas/summary.py
from pydantic import BaseModel, ConfigDict

class SummaryBase(BaseModel):
    text: str

class SummaryCreate(SummaryBase):
    lecture_id: int

class SummaryResponse(SummaryBase):
    id: int
    lecture_id: int

    model_config = ConfigDict(from_attributes=True)
