from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.job_posting import JobPosting
from app.models.interview_session import InterviewSession
from app.models.interview_turn import InterviewTurn
from app.models.feedback_report import FeedbackReport
from app.schemas.feedback import FeedbackResponse
from app.core.security import get_current_user
from app.agents.feedback_agent import feedback_graph

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/{session_id}/generate", response_model=FeedbackResponse)
def generate_feedback(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id, InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Interview must be completed before generating feedback")

    existing_feedback = db.query(FeedbackReport).filter(FeedbackReport.session_id == session_id).first()
    if existing_feedback:
        return existing_feedback

    turns = (
        db.query(InterviewTurn)
        .filter(InterviewTurn.session_id == session_id)
        .order_by(InterviewTurn.turn_number)
        .all()
    )

    if not turns:
        raise HTTPException(status_code=400, detail="No interview turns found for this session")

    job_title = "General Role"
    if session.job_id:
        job = db.query(JobPosting).filter(JobPosting.id == session.job_id).first()
        if job:
            job_title = job.title

    transcript = [
        {"turn_number": t.turn_number, "question": t.question, "answer": t.answer}
        for t in turns
    ]

    initial_state = {
        "job_title": job_title,
        "transcript": transcript,
        "feedback": {},
    }

    try:
        final_state = feedback_graph.invoke(initial_state)
        feedback_data = final_state["feedback"]
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to generate feedback. Please try again.")

    report = FeedbackReport(
        session_id=session_id,
        communication_score=feedback_data["communication_score"],
        technical_score=feedback_data["technical_score"],
        structure_score=feedback_data["structure_score"],
        summary=feedback_data["summary"],
        suggestions=feedback_data["suggestions"],
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report