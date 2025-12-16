from core.agent import build_agent, run_demo


def main():
    """
    项目入口：构建 agent，并运行一个简单 demo。

    真正的业务逻辑都拆分到了 core/config/tools 等模块中，
    这里仅作为 CLI / 脚本入口。
    """
    # 如果你只想要 agent 对象用于后续集成，可以这样用：
    agent = build_agent(show_graph=False)

    # 当前 demo：直接跑一遍 echo 工具调用
    run_demo('调用echo工具打印"Hello, World"')


if __name__ == "__main__":
    main()