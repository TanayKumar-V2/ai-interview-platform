from sqlalchemy.orm import Session
from app.models.job_posting import JobPosting
from app.core.embeddings import generate_embedding


def match_jobs_to_resume(resume_text: str, db: Session, top_k: int = 5):
    resume_embedding = generate_embedding(resume_text, input_type="search_query")

    matches = (
        db.query(JobPosting)
        .filter(JobPosting.embedding.isnot(None))
        .order_by(JobPosting.embedding.cosine_distance(resume_embedding))
        .limit(top_k)
        .all()
    )

    return matches