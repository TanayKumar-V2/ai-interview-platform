from pydantic import BaseModel
from datetime import datetime


class ResumeResponse(BaseModel):
    id: int
    file_name: str
    raw_text: str | None
    uploaded_at: datetime

    class Config:
        from_attributes = True