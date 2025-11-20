# AI 日语陪练系统

## 1. 项目简介
本项目是一个以 FastMCP 为核心的 AI 日语学习助手，支持自由对话、自动纠错、语法分析、课程学习、场景模拟以及基于用户表现的自适应难度调节。系统优先使用本地 Ollama 模型推理，并在需要时回退到 GPT，所有交互以结构化输出提供，便于前端或其他客户端直接消费。

## 2. 系统架构概述
```
MCP Server
│
├── tools/
│     ├── japanese_chat_tools.py
│     ├── lesson_tools.py
│     ├── scenario_tools.py
│     ├── user_state_tools.py
│     └── ollama_tools.py
│
├── core/
│     ├── conversation_engine.py
│     ├── ruby_utils.py
│     ├── grammar_rules.py
│     ├── grammar_engine.py
│     ├── lesson_models.py
│     ├── lesson_engine.py
│     ├── scenario_models.py
│     ├── scenario_engine.py
│     └── user_state.py
│
├── data/
│     ├── lessons.json
│     ├── scenarios.json
│     └── user_state/
│
├── server.py
└── mcp_app.py
```

## 3. 功能总览
### 3.1 Free Talk（自由对话）
- 自动生成 ruby 注音（漢字(かな) 风格）
- 自动对用户句子进行纠错与解释
- 自动翻译为中文
- 自动语法点识别并返回结构化结果
- 自动记录学习状态，驱动难度自适应

### 3.2 Lesson Engine
- 课程包含词汇与语法点，提供等级标注
- step-by-step 拆解，每个词汇/语法对应一个步骤
- 提供 MCP 工具：`get_lesson_overview` / `get_lesson_step`

### 3.3 Scenario Engine
- 预置 NPC 剧情脚本，按步骤推进
- 用户回复会触发 AI 纠错、翻译与语法分析
- 下一句 NPC 台词自动返回，便于对话串联

### 3.4 Grammar Engine
- 内置语法点数据库，支持简单包含匹配
- 统一输出标准化的语法点名称、描述与示例

### 3.5 User State Engine
- 持久化保存用户学习进度（grammar_stats）
- 根据错误率自动判断难度等级的升降
- 对话流程自动更新用户状态

## 4. 环境安装与运行
### 4.1 前置条件
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- 已安装 Ollama 及对应模型（默认 `qwen2.5:7b`）
- fastmcp / fastmcp-client 依赖

### 4.2 安装
```bash
uv sync
```

### 4.3 启动服务
```bash
uv run mcp dev server.py
```
启动后 MCP 服务器会加载所有工具模块。

### 4.4 client.py 示例
以下示例展示如何列出工具并调用 `jp_chat_turn`（含 user_id）：
```python
from fastmcp_client import MCPClient
import asyncio

async def main():
    async with MCPClient("ws://localhost:8000") as client:
        tools = await client.list_tools()
        print("已注册工具:", [t.name for t in tools])

        result = await client.call_tool(
            "jp_chat_turn",
            {"user_text": "おはよう", "user_id": "demo_user"},
        )
        print("对话结果:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. 示例
### 5.1 自由对话示例
```json
{
  "jp": "おはようございます。今日は何をしますか？",
  "zh": "早上好。今天打算做什么？",
  "user_correction": null,
  "grammar_ai": [
    {"name": "～ます", "description": "礼貌形结尾", "example": "行きます"}
  ],
  "level": "N5"
}
```

### 5.2 课程 step 示例
```json
{
  "type": "vocab",
  "index": 0,
  "total": 6,
  "data": {"jp": "はじめまして", "reading": "はじめまして", "zh": "初次见面", "example": "はじめまして、田中です。"}
}
```

### 5.3 场景 step 示例
```json
{
  "role": "npc",
  "jp": "いらっしゃいませ！",
  "zh": "欢迎光临！",
  "index": 1,
  "total": 4
}
```

## 6. 项目结构
```
project_root/
  server.py
  mcp_app.py
  core/
    conversation_engine.py
    ruby_utils.py
    grammar_rules.py
    grammar_engine.py
    lesson_models.py
    lesson_engine.py
    scenario_models.py
    scenario_engine.py
    user_state.py
  tools/
    japanese_chat_tools.py
    lesson_tools.py
    scenario_tools.py
    user_state_tools.py
    ollama_tools.py
  data/
    lessons.json
    scenarios.json
    user_state/
  examples/
    jp_chat_cli.py
    lesson_cli.py
    scenario_cli.py
  README.md
```

## 7. 扩展指南
- 新增语法点：在 `core/grammar_rules.py` 中追加 `GRAMMAR_PATTERNS` 项
- 新增课程：在 `core/lesson_models.py` 中扩展 `SAMPLE_LESSONS`，或在 `data/lessons.json` 补充数据
- 扩展场景：在 `core/scenario_models.py` 添加新的 `SAMPLE_SCENARIOS`，脚本可同步写入 `data/scenarios.json`
- 加入更强模型：修改 `core/llm_client.py` 中的 `LLMConfig` 或完善 `call_fallback` 以接入更强大的远程模型

## 8. License (MIT)
本项目使用 MIT License，详见仓库 LICENSE（如无可自行添加）。
