"""最小示例：运行 Agent 并尝试调用本地工具。"""

from main import run_agent


def demo():
    prompt = "请读取项目 README.md 的前几行"
    result = run_agent(prompt)
    for msg in result.get("messages", []):
        print(f"[{msg.type}] {msg.content}")


if __name__ == "__main__":
    demo()

