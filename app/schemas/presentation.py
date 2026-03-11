# app/schemas/presentation.py
from pydantic import BaseModel, ConfigDict

class PresentationBase(BaseModel):
    file_path: str

class PresentationCreate(PresentationBase):
    lecture_id: int

class PresentationResponse(PresentationBase):
    id: int
    lecture_id: int

    model_config = ConfigDict(from_attributes=True)
