from fastapi import FastAPI

app = FastAPI(title="AI Interview Platform API")


@app.get("/health")
def health_check():
    return {"status": "ok"}