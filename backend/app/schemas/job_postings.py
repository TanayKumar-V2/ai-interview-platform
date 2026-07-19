from pydantic import BaseModel


class JobMatchResult(BaseModel):
    id: int
    title: str
    company: str
    description: str
    location: str | None
    match_explanation: str

    class Config:
        from_attributes = True


class JobPostingResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    location: str | None

    class Config:
        from_attributes = True