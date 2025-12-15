from typing import Any, Dict

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from api.llm_interface import get_llm
from tools import TOOLS, TOOL_REGISTRY


def call_model(state: Dict[str, Any], config: RunnableConfig | None = None) -> Dict[str, Any]:
    """LLM 思考节点：向模型发送消息并获取响应。"""

    llm = get_llm().bind_tools(TOOLS)
    response = llm.invoke(state["messages"], config=config)
    return {"messages": [response]}


def call_tool(state: Dict[str, Any], config: RunnableConfig | None = None) -> Dict[str, Any]:
    """工具执行节点：根据模型输出的 tool_calls 调用本地插件。"""

    messages: list[BaseMessage] = state["messages"]
    if not messages:
        return {}

    last_message = messages[-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {}

    tool_messages: list[ToolMessage] = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {}) or {}
        tool_id = tool_call.get("id", "")
        tool = TOOL_REGISTRY.get(tool_name)

        if tool is None:
            content = f"未找到工具: {tool_name}"
        else:
            content = tool.invoke(tool_args)

        tool_messages.append(
            ToolMessage(
                tool_call_id=tool_id,
                name=tool_name or "unknown",
                content=str(content),
            )
        )

    return {"messages": tool_messages}


def decide_next_step(state: Dict[str, Any]) -> str:
    """路由逻辑：根据最新 AI 消息判断下一步。"""

    messages: list[BaseMessage] = state["messages"]
    if not messages:
        return "end"

    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
        return "action"
    return "end"


