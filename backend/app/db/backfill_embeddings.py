from app.db.database import SessionLocal
from app.models.job_posting import JobPosting
from app.core.embeddings import generate_embedding


def backfill_embeddings():
    db = SessionLocal()
    try:
        jobs = db.query(JobPosting).filter(JobPosting.embedding.is_(None)).all()

        if not jobs:
            print("No job postings need embeddings.")
            return

        for job in jobs:
            text_to_embed = f"{job.title} at {job.company}. {job.description} Requirements: {job.requirements or ''}"
            job.embedding = generate_embedding(text_to_embed, input_type="search_document")
            print(f"Generated embedding for: {job.title} at {job.company}")

        db.commit()
        print(f"Backfilled {len(jobs)} job postings.")
    finally:
        db.close()


if __name__ == "__main__":
    backfill_embeddings()