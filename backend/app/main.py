from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, resumes, jobs, interviews, feedback

app = FastAPI(title="AI Interview Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(interviews.router)
app.include_router(feedback.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}