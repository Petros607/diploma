# app/schemas/transcript.py
from pydantic import BaseModel


class TranscriptBase(BaseModel):
    text: str


class TranscriptCreate(TranscriptBase):
    lecture_id: int


class TranscriptResponse(TranscriptBase):
    id: int
    lecture_id: int

    class Config:
        from_attributes = True
