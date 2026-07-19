from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class FeedbackReport(Base):
    __tablename__ = "feedback_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    communication_score = Column(Integer, nullable=False)
    technical_score = Column(Integer, nullable=False)
    structure_score = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    suggestions = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())