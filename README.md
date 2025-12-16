## 项目简介

这是一个基于 **LangGraph** 的轻量级 Agent Demo，目标是：

- **方便接入各种本地 / 远程工具**（通过 Python `@tool` + Registry 管理）；
- 提供一个 **清晰的项目骨架**，可以在此基础上快速扩展为自己的 Agent 服务；
- 将配置、LLM 初始化、Agent 逻辑、工具实现 **模块化解耦**，便于维护与复用。

当前示例包含一个简单的 `echo` 工具，通过 LangGraph 的状态机自动决定是否调用工具，并在终端中打印结果。

## 项目结构

```text
PluginOS/
├─ main.py                # 程序入口，只负责构建 agent 并运行 demo
├─ config/
│  ├─ settings.py         # 运行时配置（LLM_API_KEY、MODEL 等），基于 pydantic-settings
│  └─ __init__.py
├─ core/
│  ├─ llm_init.py         # get_llm(): 封装 LLM 初始化逻辑
│  ├─ agent.py            # LangGraph StateGraph 构建、agent 编译与 demo 运行
│  └─ __init__.py
├─ tools/
│  ├─ local_plugins.py    # 使用 @tool 定义的本地插件（例如 echo）
│  └─ __init__.py         # 导出 tools / tools_registry，供 agent 使用
├─ requirements.txt
└─ README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量 / `.env`

项目使用 `pydantic-settings` 从环境变量中读取 LLM 配置，前缀为 `LLM_`。你可以在项目根目录新建 `.env` 文件（或直接设置系统环境变量）：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1    # 可选，自行替换为实际地址
LLM_MODEL=deepseek-chat                  # 或其他兼容模型名称
LLM_TEMPERATURE=0
LLM_REQUEST_TIMEOUT=60
```

> **注意**：`LLM_API_KEY` 不能为空，否则 `core/llm_init.py` 中的 `get_llm()` 会抛出异常明确提示。

### 3. 运行 Demo

```bash
python main.py
```

`main.py` 会：

- 通过 `build_agent(show_graph=False)` 构建一个 LangGraph Agent；
- 调用 `run_demo('调用echo工具打印"Hello, World"')`；
- Agent 内部会自动决定是否调用 `echo` 工具，并在终端中打印思考过程与工具输出。

## 核心设计说明

- **配置层（config）**

  - 使用 `Settings` 统一管理 LLM 相关配置（API Key、Base URL、模型、温度、超时等）；
  - 通过 `get_settings()` 做懒加载与缓存，避免多次解析环境变量。

- **LLM 初始化（core/llm_init.py）**

  - `get_llm()` 封装具体模型创建逻辑，对上层只暴露统一接口；
  - 方便后续切换到其他 LLM 提供商或增加路由/重试等高级逻辑。

- **Agent 图（core/agent.py）**

  - 基于 `StateGraph` 定义 `MessagesState`、`llm_call`、`tool_node`、`should_continue` 这几个核心节点；
  - `build_agent()` 负责创建并编译图，`run_demo()` 提供一个最小可运行的样例；
  - 可选 `show_graph=True` 在 Notebook 环境下可视化 Agent 结构。

- **工具系统（tools）**
  - 使用 `@tool` 装饰器定义工具（如 `echo`）；
  - 使用 `tools_registry = {tool.name: tool for tool in tools}` 做集中管理，便于按名称查找并调用；
  - 将“工具定义”与“Agent 逻辑”解耦，方便后续自由扩展。

## 如何新增一个工具

1. **在 `tools/local_plugins.py` 中新增函数并使用 `@tool` 装饰**：
   - 函数要有清晰的签名和 docstring，便于 LLM 理解。
2. **把新工具加入 `tools` 列表**：
   ```python
   tools = [echo, your_new_tool, ...]
   tools_registry = {tool.name: tool for tool in tools}
   ```
3. **在系统提示词中描述工具能力（可选）**：
   - 如果需要更精细地引导 LLM 什么时候调用该工具，可以修改 `core/agent.py` 中 `SystemMessage` 的内容。

这样，Agent 就可以在推理过程中自动选择是否调用你新增的工具。

## TODO / 规划

- **工具层**

  - [ ] 设计统一的工具分类与命名规范（如 `fs.read_file`、`web.search` 等）。
  - [ ] 增加更多示例工具（文件系统、HTTP 请求、数据库、系统命令等）。
  - [ ] 支持基于配置的“开关某些工具”（例如通过环境变量/配置文件选择启用哪些工具）。

- **Agent 能力**

  - [ ] 支持多轮对话与持久化记忆（将 `MessagesState` 落地到存储，如 SQLite / Redis）。
  - [ ] 增加错误恢复与重试机制（工具调用失败后的回退策略）。
  - [ ] 支持更复杂的决策路由（不止 `tool_node` / `END`，例如多 Agent 协作）。

- **工程化 / 接入方式**

  - [ ] 提供 CLI 接口（如 `python main.py "帮我xxx"`，直接从命令行传入用户指令）。
  - [ ] 提供 HTTP API（FastAPI / Flask），方便其他服务接入该 Agent。
  - [ ] 编写更多文档示例：如“如何在现有项目里嵌入这个 Agent”。

- **配置与部署**
  - [ ] 支持多环境配置（dev / prod），在 `Settings` 中增加环境区分。
  - [ ] 编写 Dockerfile / 部署说明，便于一键部署。

## 后续方向

本项目目前是一个**聚焦 LangGraph + 工具调用**的最小骨架，适合作为个人 Agent 项目的起点。

如果你有更具体的目标（例如：自动化运维助手、数据分析 Agent、个人知识库问答等），可以在：

- `tools/` 下增加领域工具；
- `core/agent.py` 中定制系统提示词与决策逻辑；
- `config/` 中扩展更多与业务相关的配置。
