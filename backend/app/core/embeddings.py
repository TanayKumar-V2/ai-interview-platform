import os
import cohere

co = cohere.Client(os.getenv("COHERE_API_KEY"))


def generate_embedding(text: str, input_type: str = "search_document") -> list[float]:
    response = co.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type=input_type,
    )
    return response.embeddings[0]

def generate_match_explanation(resume_text: str, job_title: str, job_company: str, job_description: str, job_requirements: str) -> str:
    prompt = f"""You are a career advisor. Compare this candidate's resume to the job below.

RESUME:
{resume_text[:3000]}

JOB TITLE: {job_title}
COMPANY: {job_company}
JOB DESCRIPTION: {job_description}
JOB REQUIREMENTS: {job_requirements}

In 3-4 sentences, explain why this candidate is or isn't a good fit, and mention 1-2 specific skill gaps if any exist. Be concise and direct."""

    response = co.chat(
        message=prompt,
        model="command-r",
        temperature=0.3,
    )
    return response.text