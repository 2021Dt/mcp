# AI 日语陪练系统（重构版）

## 项目概览
本项目提供面向 MCP 的 AI 日语陪练能力，覆盖自由对话、课程分步讲解、场景演练与用户等级追踪。当前架构经过分层重构，明确了**引擎 / 服务 / 工具**边界，支持可插拔的 AI 后端与统一日志体系。

## 目录结构
```
project_root/
├── core/
│   ├── models.py                # TypedDict 数据模型
│   ├── engines/                 # 业务引擎（纯逻辑）
│   │   ├── conversation_engine.py
│   │   ├── grammar_engine.py
│   │   ├── grammar_rules.py
│   │   ├── lesson_engine.py
│   │   ├── scenario_engine.py
│   │   ├── user_state_engine.py
│   │   └── ruby_utils.py
│   ├── services/                # AI 与 Agent 层
│   │   ├── ai_client.py
│   │   ├── ai_client_utils.py
│   │   └── agent_runner.py
│   └── utils/
│       ├── dp_log.py            # 统一日志工厂
│       └── helpers.py
├── tools/                       # MCP 工具层（无业务逻辑）
│   ├── japanese_chat_tools.py
│   ├── lesson_tools.py
│   ├── scenario_tools.py
│   ├── user_state_tools.py
│   ├── grammar_tools.py
│   └── ollama_tools.py
├── repl.py                      # 本地 REPL 客户端（AgentRunner）
├── server.py                    # MCP Server 入口
└── mcp_app.py                   # FastMCP 实例
```

### 模块职责
- **core.models**：集中声明所有 TypedDict 数据结构。
- **core.engines**：封装教学逻辑（对话、语法检测、课程拆分、场景推进、用户状态），仅依赖模型与工具函数。
- **core.services**：AI 客户端与 Agent 循环，负责模型选择、工具调用与消息流转。
- **core.utils**：日志工厂与通用工具函数。
- **tools/**：仅负责参数转发到引擎/服务，不包含业务逻辑、判断或解析。
- **server.py**：启动 MCP 并注册工具，初始化全局日志输出。
- **repl.py**：通过 FastMCP Client + AgentRunner 统一调用工具与 AI。

## AIClient / AgentRunner 架构
```
AgentRunner.run(prompt)
    └── AIClient.chat(...)  # Ollama / API 模式切换
          └── MCP 工具定义通过 convert_mcp_tools_to_ollama 注入
    └── MCPClient           # 按需调用工具并回填 tool 消息
```
- **AIClient**：
  - `mode="ollama"`：使用本地 Ollama，默认模型 `qwen2.5:7b`。
  - `mode="api"`：预留商业 API（GPT / DeepSeek / Doubao 等），当前抛出 `NotImplementedError`，可在 `_chat_api` 中扩展。
- **AgentRunner**：
  - 负责构建初始对话消息，列出 MCP 工具并转换为 Ollama 工具规范。
  - 自动循环处理工具调用（上限 8 次），将工具输出追加到消息历史。

## 工具层约束
- 工具仅做**参数转发**：收到 MCP 请求 → 调用对应引擎/服务函数 → 返回结果。
- 禁止在工具内加入日志、分支判断或 AI 推理逻辑。
- 业务逻辑全部在 `core/engines` 与 `core/services` 中实现。

## 切换本地模型 / 商业 API
- 默认使用本地 Ollama：`AIClient(mode="ollama", model="qwen2.5:7b")`。
- 如需商业 API：实例化 `AIClient(mode="api", model="<remote_model>")` 并实现 `_chat_api`（可调用 OpenAI、DeepSeek 等 SDK）。
- MCP 工具 `ollama_chat` 亦复用 `AIClient`，确保调用链一致。

## 日志系统
- 全局控制台在 `server.py` 顶部通过 `LogFactory.configure_global(enable_console=True)` 启用。
- 各引擎内获取模块化 logger：
  ```python
  from core.utils.dp_log import LogFactory
  logger = LogFactory.get_logger(__name__)
  ```
- 日志按模块落盘至 `logs/<module>/<date>.log`，默认保留 7 天，午夜切分。

## REPL 使用
- 启动：`python repl.py`
- 特性：
  - 自动导入全部工具，保证 MCP 注册完整。
  - `/lesson`、`/scenario`、`/state` 等命令直接通过 FastMCP Client 调用工具。
  - 普通文本走 `AgentRunner.run`，由 AIClient + MCP 工具协同完成。

示例操作：
```
$ python repl.py
[JP-AI] > /lesson n5_lesson_01
[JP-AI] > おはよう
```

## MCP Server 运行
```
uv run mcp dev server.py
```
启动后 FastMCP 会加载所有工具模块，客户端即可通过 WebSocket 访问。
