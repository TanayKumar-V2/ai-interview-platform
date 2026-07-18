from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.job_postings import JobMatchResponse
from app.core.security import get_current_user
from app.core.job_matcher import match_jobs_to_resume

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/match/{resume_id}", response_model=list[JobMatchResponse])
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

    matches = match_jobs_to_resume(resume.raw_text, db)
    return matches