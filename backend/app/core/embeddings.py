import os
import cohere
import json

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
        model="command-a-03-2025",
        temperature=0.3,
    )
    return response.text

def generate_interview_question(job_title: str, job_description: str, previous_turns: list[dict], turn_number: int) -> str:
    history_text = ""
    for turn in previous_turns:
        history_text += f"Q{turn['turn_number']}: {turn['question']}\nA{turn['turn_number']}: {turn['answer']}\n\n"

    if turn_number == 1:
        prompt = f"""You are conducting a mock job interview for the role of {job_title}.
Job description: {job_description}

Ask an opening interview question — something that lets the candidate introduce their relevant background. Ask only the question, nothing else."""
    else:
        prompt = f"""You are conducting a mock job interview for the role of {job_title}.
Job description: {job_description}

Conversation so far:
{history_text}

Based on the candidate's previous answer, ask a relevant follow-up or a new interview question that probes deeper into their skills or experience. Ask only the question, nothing else."""

    response = co.chat(
        message=prompt,
        model="command-a-03-2025",
        temperature=0.6,
    )
    return response.text.strip()




def generate_interview_feedback(job_title: str, transcript: list[dict]) -> dict:
    transcript_text = ""
    for turn in transcript:
        transcript_text += f"Q{turn['turn_number']}: {turn['question']}\nA{turn['turn_number']}: {turn['answer']}\n\n"

    prompt = f"""You are an expert interview coach. Review this mock interview transcript for a {job_title} role.

TRANSCRIPT:
{transcript_text}

Evaluate the candidate on three dimensions, each scored 1-10:
- communication_score: clarity, confidence, and structure of spoken responses
- technical_score: depth and accuracy of technical/domain knowledge shown
- structure_score: how well-organized and complete each answer was (e.g. STAR method, clear reasoning)

Also provide:
- summary: 2-3 sentences on overall performance
- suggestions: 2-3 specific, actionable improvements

Respond ONLY with valid JSON in this exact format, nothing else:
{{"communication_score": <int>, "technical_score": <int>, "structure_score": <int>, "summary": "<text>", "suggestions": "<text>"}}"""

    response = co.chat(
        message=prompt,
        model="command-a-03-2025",
        temperature=0.3,
    )

    cleaned = response.text.strip().strip("```json").strip("```").strip()
    return json.loads(cleaned)