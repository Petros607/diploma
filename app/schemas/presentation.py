# app/schemas/presentation.py
from pydantic import BaseModel


class PresentationBase(BaseModel):
    file_path: str


class PresentationCreate(PresentationBase):
    lecture_id: int


class PresentationResponse(PresentationBase):
    id: int
    lecture_id: int

    class Config:
        from_attributes = True
