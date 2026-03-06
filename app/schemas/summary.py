# app/schemas/summary.py
from pydantic import BaseModel


class SummaryBase(BaseModel):
    text: str


class SummaryCreate(SummaryBase):
    lecture_id: int


class SummaryResponse(SummaryBase):
    id: int
    lecture_id: int

    class Config:
        from_attributes = True
