from langgraph.graph import END, START, StateGraph
from .nodes import call_model, call_tool, decide_next_step
from .state import GraphState


def create_graph():
    """构建并返回编译后的 LangGraph 应用。"""

    builder = StateGraph(GraphState)
    builder.add_node("model", call_model)
    builder.add_node("action", call_tool)

    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", decide_next_step, {"action": "action", "end": END})
    builder.add_edge("action", "model")

    return builder.compile()


__all__ = ["create_graph"]

