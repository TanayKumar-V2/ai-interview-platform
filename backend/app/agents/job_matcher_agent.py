from typing import TypedDict
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.models.job_posting import JobPosting
from app.core.embeddings import generate_embedding, generate_match_explanation


class JobMatchState(TypedDict):
    resume_text: str
    db: Session
    top_k: int
    matched_jobs: list
    results: list


def search_jobs_node(state: JobMatchState) -> JobMatchState:
    resume_embedding = generate_embedding(state["resume_text"], input_type="search_query")

    matches = (
        state["db"].query(JobPosting)
        .filter(JobPosting.embedding.isnot(None))
        .order_by(JobPosting.embedding.cosine_distance(resume_embedding))
        .limit(state["top_k"])
        .all()
    )

    state["matched_jobs"] = matches
    return state


def explain_matches_node(state: JobMatchState) -> JobMatchState:
    results = []
    for job in state["matched_jobs"]:
        explanation = generate_match_explanation(
            resume_text=state["resume_text"],
            job_title=job.title,
            job_company=job.company,
            job_description=job.description,
            job_requirements=job.requirements or "",
        )
        results.append({
            "job": job,
            "explanation": explanation,
        })

    state["results"] = results
    return state


def build_job_matcher_graph():
    graph = StateGraph(JobMatchState)

    graph.add_node("search_jobs", search_jobs_node)
    graph.add_node("explain_matches", explain_matches_node)

    graph.set_entry_point("search_jobs")
    graph.add_edge("search_jobs", "explain_matches")
    graph.add_edge("explain_matches", END)

    return graph.compile()


job_matcher_graph = build_job_matcher_graph()