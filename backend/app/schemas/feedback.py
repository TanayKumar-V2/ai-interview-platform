from pydantic import BaseModel
from datetime import datetime


class FeedbackResponse(BaseModel):
    id: int
    session_id: int
    communication_score: int
    technical_score: int
    structure_score: int
    summary: str
    suggestions: str
    created_at: datetime

    class Config:
        from_attributes = True