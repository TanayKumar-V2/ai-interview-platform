from pydantic import BaseModel
from datetime import datetime


class StartInterviewRequest(BaseModel):
    job_id: int | None = None


class AnswerRequest(BaseModel):
    answer: str


class InterviewTurnResponse(BaseModel):
    session_id: int
    turn_number: int
    question: str
    status: str


class InterviewSessionResponse(BaseModel):
    id: int
    status: str
    started_at: datetime

    class Config:
        from_attributes = True