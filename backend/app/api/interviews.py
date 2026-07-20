from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.job_posting import JobPosting
from app.models.interview_session import InterviewSession
from app.models.interview_turn import InterviewTurn
from app.schemas.interview import StartInterviewRequest, AnswerRequest, InterviewTurnResponse
from app.core.security import get_current_user
from app.agents.interview_agent import interview_graph
from app.schemas.interview import InterviewSessionResponse
from app.models.feedback_report import FeedbackReport
from app.schemas.interview import InterviewDetailResponse
from app.models.proctoring_flag import ProctoringFlag
from app.schemas.interview import FlagRequest

router = APIRouter(prefix="/interviews", tags=["interviews"])

MAX_TURNS = 5


@router.post("/start", response_model=InterviewTurnResponse)
def start_interview(
    request: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_title = "General Role"
    job_description = "A general practice interview covering common professional skills."

    if request.job_id:
        job = db.query(JobPosting).filter(JobPosting.id == request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found")
        job_title = job.title
        job_description = job.description

    session = InterviewSession(
        user_id=current_user.id,
        job_id=request.job_id,
        status="in_progress",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    initial_state = {
        "job_title": job_title,
        "job_description": job_description,
        "previous_turns": [],
        "turn_number": 1,
        "next_question": "",
    }
    final_state = interview_graph.invoke(initial_state)

    turn = InterviewTurn(
        session_id=session.id,
        turn_number=1,
        question=final_state["next_question"],
        answer=None,
    )
    db.add(turn)
    db.commit()

    return {
        "session_id": session.id,
        "turn_number": 1,
        "question": final_state["next_question"],
        "status": "in_progress",
    }
    
@router.post("/{session_id}/answer", response_model=InterviewTurnResponse)
def submit_answer(
    session_id: int,
    request: AnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id, InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="This interview has already ended")

    current_turn = (
        db.query(InterviewTurn)
        .filter(InterviewTurn.session_id == session_id, InterviewTurn.answer.is_(None))
        .order_by(InterviewTurn.turn_number.desc())
        .first()
    )

    if not current_turn:
        raise HTTPException(status_code=400, detail="No pending question to answer")

    current_turn.answer = request.answer
    db.commit()

    all_turns = (
        db.query(InterviewTurn)
        .filter(InterviewTurn.session_id == session_id)
        .order_by(InterviewTurn.turn_number)
        .all()
    )

    if len(all_turns) >= MAX_TURNS:
        session.status = "completed"
        db.commit()
        return {
            "session_id": session.id,
            "turn_number": current_turn.turn_number,
            "question": "Interview complete. Thank you for your responses!",
            "status": "completed",
        }

    job_title = "General Role"
    job_description = "A general practice interview covering common professional skills."
    if session.job_id:
        job = db.query(JobPosting).filter(JobPosting.id == session.job_id).first()
        if job:
            job_title = job.title
            job_description = job.description

    previous_turns = [
        {"turn_number": t.turn_number, "question": t.question, "answer": t.answer}
        for t in all_turns
    ]

    next_turn_number = current_turn.turn_number + 1

    initial_state = {
        "job_title": job_title,
        "job_description": job_description,
        "previous_turns": previous_turns,
        "turn_number": next_turn_number,
        "next_question": "",
    }
    final_state = interview_graph.invoke(initial_state)

    new_turn = InterviewTurn(
        session_id=session.id,
        turn_number=next_turn_number,
        question=final_state["next_question"],
        answer=None,
    )
    db.add(new_turn)
    db.commit()

    return {
        "session_id": session.id,
        "turn_number": next_turn_number,
        "question": final_state["next_question"],
        "status": "in_progress",
    }
    
@router.get("/", response_model=list[InterviewSessionResponse])
def list_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.started_at.desc())
        .all()
    )
    return sessions

@router.get("/{session_id}", response_model=InterviewDetailResponse)
def get_interview_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id, InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    turns = (
        db.query(InterviewTurn)
        .filter(InterviewTurn.session_id == session_id)
        .order_by(InterviewTurn.turn_number)
        .all()
    )

    feedback_report = db.query(FeedbackReport).filter(FeedbackReport.session_id == session_id).first()

    feedback_dict = None
    if feedback_report:
        feedback_dict = {
            "communication_score": feedback_report.communication_score,
            "technical_score": feedback_report.technical_score,
            "structure_score": feedback_report.structure_score,
            "summary": feedback_report.summary,
            "suggestions": feedback_report.suggestions,
        }

    return {
        "id": session.id,
        "status": session.status,
        "started_at": session.started_at,
        "ended_at": session.ended_at,
        "turns": turns,
        "feedback": feedback_dict,
    }

@router.post("/{session_id}/flag")
def create_flag(
    session_id: int,
    request: FlagRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id, InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    flag = ProctoringFlag(
        session_id=session_id,
        flag_type=request.flag_type,
        message=request.message,
    )
    db.add(flag)
    db.commit()

    return {"status": "logged"}