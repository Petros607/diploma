from pydantic import BaseModel, ConfigDict

class TranscriptBase(BaseModel):
    text: str

class TranscriptCreate(TranscriptBase):
    lecture_id: int

class TranscriptResponse(TranscriptBase):
    id: int
    lecture_id: int

    model_config = ConfigDict(from_attributes=True)
