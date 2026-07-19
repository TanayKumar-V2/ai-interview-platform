from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.core.embeddings import generate_interview_question


class InterviewState(TypedDict):
    job_title: str
    job_description: str
    previous_turns: list[dict]
    turn_number: int
    next_question: str


def generate_question_node(state: InterviewState) -> InterviewState:
    question = generate_interview_question(
        job_title=state["job_title"],
        job_description=state["job_description"],
        previous_turns=state["previous_turns"],
        turn_number=state["turn_number"],
    )
    state["next_question"] = question
    return state


def build_interview_graph():
    graph = StateGraph(InterviewState)

    graph.add_node("generate_question", generate_question_node)

    graph.set_entry_point("generate_question")
    graph.add_edge("generate_question", END)

    return graph.compile()


interview_graph = build_interview_graph()