from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class ProctoringFlag(Base):
    __tablename__ = "proctoring_flags"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    flag_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    flagged_at = Column(DateTime(timezone=True), server_default=func.now())