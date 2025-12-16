from typing import Literal

from langchain.messages import SystemMessage, AnyMessage, HumanMessage
from langchain_core.messages import ToolMessage
from typing_extensions import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, START, END

from tools import tools_registry
from .llm_init import get_llm


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


def _build_llm():
    """内部封装，避免在模块导入时就真正初始化模型。"""
    return get_llm()


def llm_call(state: dict):
    """LLM 决定是否调用工具。"""

    model = _build_llm()
    return {
        "messages": [
            model.invoke(
                [
                    SystemMessage(
                        content="你是一个有用的助手，负责调用 echo 工具打印信息。"
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def tool_node(state: dict):
    """执行工具调用。"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_registry[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """决定是否继续循环或停止，基于 LLM 是否进行了工具调用。"""

    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tool_node"
    return END


def build_agent(show_graph: bool = False):
    """
    构建并返回一个 LangGraph agent。

    :param show_graph: 是否返回前打印图结构（需要在 Notebook / 支持图片的环境中）。
    """
    agent_builder = StateGraph(MessagesState)

    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)

    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges(
        "llm_call",
        should_continue,
        ["tool_node", END],
    )
    agent_builder.add_edge("tool_node", "llm_call")

    agent = agent_builder.compile()

    if show_graph:
        try:
            from IPython.display import Image, display

            display(Image(agent.get_graph(xray=True).draw_mermaid_png()))
        except Exception:
            # 在非 Notebook 或无图形环境下静默跳过
            pass

    return agent


def run_demo(prompt: str = "调用echo工具打印\"Hello, World\""):
    """
    一个简单的 demo 入口，用于在代码中快速验证 agent 是否工作正常。
    """
    agent = build_agent(show_graph=False)
    messages = [HumanMessage(content=prompt)]
    result = agent.invoke({"messages": messages})
    for m in result["messages"]:
        m.pretty_print()


