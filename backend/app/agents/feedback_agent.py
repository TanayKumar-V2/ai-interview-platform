from typing import TypedDict
from app.core.embeddings import generate_interview_feedback
from langgraph.graph import StateGraph, END


class FeedbackState(TypedDict):
    job_title: str
    transcript: list[dict]
    feedback: dict


def generate_feedback_node(state: FeedbackState) -> FeedbackState:
    feedback = generate_interview_feedback(
        job_title=state["job_title"],
        transcript=state["transcript"],
    )
    state["feedback"] = feedback
    return state


def build_feedback_graph():
    graph = StateGraph(FeedbackState)

    graph.add_node("generate_feedback", generate_feedback_node)

    graph.set_entry_point("generate_feedback")
    graph.add_edge("generate_feedback", END)

    return graph.compile()


feedback_graph = build_feedback_graph()