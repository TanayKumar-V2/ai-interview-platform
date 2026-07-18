from fastapi import FastAPI
from app.api import auth,resumes,jobs

app = FastAPI(title="AI Interview Platform API")

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}