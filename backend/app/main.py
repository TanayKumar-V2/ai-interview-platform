from fastapi import FastAPI
from app.api import auth,resumes,jobs,interviews,feedback

app = FastAPI(title="AI Interview Platform API")

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(interviews.router)
app.include_router(feedback.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}