阶段一：定义状态 (core/state.py)

阶段二：定义工具和模型 (tools/local_plugins.py & api/llm_interface.py)

1. **定义工具 (Tools)**：使用 LangChain 的 `@tool` 装饰器。
2. **初始化 LLM**：使用用户提供的 API 配置。

阶段三：构建图 (core/graph.py & core/nodes.py)

这是核心的主控逻辑。图中有两个主要节点：`call_model` 和 `call_tool`。

1. **定义节点函数 (core/nodes.py)**：
   - **`call_model` 节点** (负责思考/推理)：
     - 接收 `GraphState`。
     - 调用 LLM (`llm.invoke(state['messages'])`)。
     - 将 LLM 的响应（包含文本或 `tool_calls`）存回 `messages`。
   - **`call_tool` 节点** (负责行动/执行)：
     - 接收 `GraphState`。
     - 从 LLM 的最新消息中解析出 `tool_calls`。
     - 执行对应的本地函数（`read_local_file(...)`）。
     - 创建新的 **`ToolMessage`** (执行结果)，并存回 `messages`。
2. **定义路由函数 (Decision)**：
   - 检查 `call_model` 节点的输出。
   - **如果** LLM 响应中包含 `tool_calls`，返回 `"continue_action"`（转向 `call_tool` 节点）。
   - **否则**（纯文本回复或结束信号），返回 `"end_conversation"`（转向 `END`）。
3. **组装图 (core/graph.py)**

阶段四：运行 (main.py)

| 架构图模块    | 核心功能                         | LangChain / LangGraph 对应组件  | 技术栈/实现细节                                             |
| ------------- | -------------------------------- | ------------------------------- | ----------------------------------------------------------- |
| Orchestrator  | 任务循环、状态维护、决策流转     | LangGraph StateGraph            | Python 代码实现状态机（节点和边）。                         |
| LLM API       | 模型推理、函数调用/工具调用      | BaseChatModel (如 ChatOpenAI)   | 接收用户提供的 API Key 和 Base URL 进行初始化。             |
| PromptEng     | 组装 Prompt (系统指令、工具描述) | BaseChatModel .bind_tools()     | LangChain 自动将 Python 函数转换为 JSON Schema 并传入 LLM。 |
| Tool Registry | 插件定义 (Schema)                | @tool 装饰器                    | 将本地 Python 函数标记为 LLM 可用的工具。                   |
| Executor      | 本地代码执行                     | AgentExecutor 或自定义 ToolNode | 接收 LLM 传来的函数名和参数，并执行本地 Python 函数。       |
| History       | 对话历史/上下文                  | GraphState                      | 使用 TypedDict 定义图的状态，包含 messages 列表。           |

```
agent_project/
├── core/
│   ├── __init__.py
│   ├── graph.py            # LangGraph 主控逻辑 (Orchestrator)
│   ├── state.py            # 定义 GraphState (记忆/上下文)
│   └── nodes.py            # 定义图中的节点 (LLM调用, 工具执行等)
│
├── tools/
│   ├── __init__.py         # 导出所有工具
│   ├── local_plugins.py    # 你的本地插件 (如 read_file, exec_script)
│   └── base_tools.py       # 可能的通用工具 (如 web_search)
│
├── api/
│   └── llm_interface.py    # LLM 模型初始化和抽象
│
├── config/
│   └── settings.py         # 配置管理 (API Key, Base URL)
│
├── main.py                 # 程序入口，加载配置，运行 Agent
└── requirements.txt
```




```
┌───────────────┐
│    用户输入    │
│   (User)      │
└───────┬───────┘
        │ 1. 任务输入
        ▼
┌───────────────────────┐
│   main.py 程序入口    │
│   (Main)              │
└───────┬─────────┬─────┘
        │2. 初始化  │3. 加载配置
        │  State   │
        ▼          ▼
┌──────────────────┐   ┌─────────────────────────┐
│   GraphState     │   │   配置层                  │
│ (消息历史/上下文)│   │ API Key / Base URL       │
└─────────┬────────┘   └─────────────────────────┘
          │
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│               LangGraph 运行时 (Agent Core)              │
│                                                         │
│   ┌─────────────────────────────────────────────────┐  │
│   │          LangGraph StateGraph (Graph)            │  │
│   └───────────────┬─────────────────────────────────┘  │
│                   │ 4. 初始状态                       │
│                   ▼                                   │
│     ┌───────────────────────────────┐                │
│     │ Agent Node / call_model        │                │
│     │ (LLM 思考)                     │                │
│     └───────────────┬───────────────┘                │
│                     │5. messages + tool_schema        │
│                     ▼                                 │
│        ┌────────────────────────────────────┐        │
│        │        外部 LLM 服务                │        │
│        │   用户提供的 LLM API               │        │
│        └────────────────────────────────────┘        │
│                     ▲                                 │
│                     │6. 文本 / tool_calls             │
│     ┌───────────────┴───────────────┐                │
│     │ 更新 State (消息历史)          │                │
│     └───────────────┬───────────────┘                │
│                     │7. 更新状态                     │
│                     ▼                                 │
│              ┌──────────────┐                        │
│              │    Router    │                        │
│              │ 决策下一步   │                        │
│              └───────┬──────┘                        │
│          9a.需要工具 │        9b.任务完成             │
│                     │                                 │
│                     ▼                                 ▼
│     ┌───────────────────────────────┐          ┌──────────┐
│     │ Action Node / call_tool        │          │   END    │
│     │ (本地执行)                     │          └────┬─────┘
│     └───────────────┬───────────────┘               │14.结果
│                     │10. tool_calls                  │
│                     ▼                                │
│     ┌─────────────────────────────────────────┐     │
│     │           本地插件系统                  │     │
│     │                                         │     │
│     │  ┌───────────────────────────────────┐ │     │
│     │  │  Python @tool Registry             │◄┼─────┘
│     │  └──────────────┬────────────────────┘ │
│     │                 │ tools_schema          │
│     │  ┌──────────────▼────────────────────┐ │
│     │  │ local_plugins.py                   │ │
│     │  │ 本地插件函数实现                   │ │
│     │  └───────────────────────────────────┘ │
│     └───────────────────┬─────────────────────┘
│                         │11. 执行结果
│                         ▼
│     ┌───────────────────────────────────────┐
│     │ ToolMessage 写回 GraphState            │
│     └───────────────┬───────────────────────┘
│                     │12. 追加历史
│                     ▼
│          回到 Agent Node (继续思考循环)
│
└─────────────────────────────────────────────────────────┘

```

