import argparse
import json
from typing import Any, Dict
from langchain_core.messages import HumanMessage
from config.settings import get_settings
from core.graph import create_graph


def run_agent(prompt: str) -> Dict[str, Any]:
    app = create_graph()
    state = {"messages": [HumanMessage(content=prompt)]}
    return app.invoke(state)


def main():
    parser = argparse.ArgumentParser(description="LangGraph Agent Demo")
    parser.add_argument("prompt", type=str, nargs="?", help="用户输入的任务或问题")
    args = parser.parse_args()

    if not args.prompt:
        parser.error("请提供 prompt，如: python main.py \"读取 README\"")

    settings = get_settings()
    if not settings.api_key:
        print("警告：未设置 LLM_API_KEY，某些模型可能无法调用。")

    result = run_agent(args.prompt)
    messages = result.get("messages", [])
    print(json.dumps([m.dict() for m in messages], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

