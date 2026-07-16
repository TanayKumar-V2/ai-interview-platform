from fastapi import FastAPI
from app.api import auth,resumes

app = FastAPI(title="AI Interview Platform API")

app.include_router(auth.router)
app.include_router(resumes.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}