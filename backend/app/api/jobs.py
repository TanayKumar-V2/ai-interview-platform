from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.job_postings import JobMatchResult
from app.core.security import get_current_user
from app.agents.job_matcher_agent import job_matcher_graph

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/match/{resume_id}", response_model=list[JobMatchResult])
def get_job_matches(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume.raw_text:
        raise HTTPException(status_code=400, detail="Resume has no extracted text")

    initial_state = {
        "resume_text": resume.raw_text,
        "db": db,
        "top_k": 3,
        "matched_jobs": [],
        "results": [],
    }

    final_state = job_matcher_graph.invoke(initial_state)

    response = [
        {
            "id": r["job"].id,
            "title": r["job"].title,
            "company": r["job"].company,
            "description": r["job"].description,
            "location": r["job"].location,
            "match_explanation": r["explanation"],
        }
        for r in final_state["results"]
    ]

    return response