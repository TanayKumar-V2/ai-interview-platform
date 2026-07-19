from fastapi import FastAPI
from app.api import auth,resumes,jobs,interviews

app = FastAPI(title="AI Interview Platform API")

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(interviews.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}