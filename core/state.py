from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """定义 LangGraph 中流转的状态。"""

    messages: Annotated[list[BaseMessage], add_messages]


