# AI 日语陪练系统

## 1. 项目简介
本项目是一个基于 FastMCP 的 AI 日语学习助手，提供自由对话、自动纠错、语法分析、分步课程、场景模拟以及基于用户表现的自适应难度调节。系统优先调用本地 Ollama 模型（默认 `qwen2.5:7b`），必要时可回退到兜底模型。所有接口均通过 MCP 工具暴露，返回结构化数据，方便前端或其他客户端直接消费。

## 2. 系统架构概述
```
MCP Server（server.py -> mcp_app.py -> tools/*）
│
├── tools/                 # MCP 工具定义层，负责把核心逻辑暴露为 API
│     ├── japanese_chat_tools.py   # 自由对话工具
│     ├── grammar_tools.py         # 语法识别工具
│     ├── lesson_tools.py          # 课程概览与步骤工具
│     ├── scenario_tools.py        # 场景脚本工具
│     ├── user_state_tools.py      # 用户状态读写工具
│     └── ollama_tools.py          # 封装 Ollama 聊天能力
│
├── core/                  # 核心业务与算法层
│     ├── conversation_engine.py   # 单轮对话流程：纠错、回复、语法、翻译、状态
│     ├── ruby_utils.py           # 日文假名注音占位逻辑
│     ├── grammar_rules.py        # 硬编码语法规则库
│     ├── grammar_engine.py       # 语法点匹配引擎
│     ├── lesson_models.py        # 课程数据模型与样例
│     ├── lesson_engine.py        # 课程拆步骤逻辑
│     ├── scenario_models.py      # 场景剧本模型与样例
│     ├── scenario_engine.py      # 场景执行与对话推进
│     ├── user_state.py           # 用户状态持久化与等级决策
│     └── llm_client.py           # LLM 调度（Ollama 优先 + 兜底）
│
├── data/                  # 预置数据与用户状态
│     ├── lessons.json
│     ├── scenarios.json
│     └── user_state/
│
├── examples/              # CLI 调用示例
├── server.py              # FastMCP 入口，注册工具
└── mcp_app.py             # FastMCP 实例
```

### 2.1 数据流概要
1. 客户端通过 MCP 连接 `server.py` 暴露的工具。
2. 工具层把请求转发到 `core` 引擎完成实际逻辑。
3. 引擎调用 `llm_client` 选择本地 Ollama 或兜底模型。
4. 结果在需要时写入 `data/user_state/*.json`，并以结构化形式返回。

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

## 5. 核心数据模型（`core/models.py`）
### 5.1 会话 / 语法相关类型
- `GrammarPoint`：AI 回复中识别到的语法点，字段：
  - `name`：语法点名称，如“～うちに”。
  - `description`：中文解释，描述语法含义或使用场景。
  - `example`：示例句，帮助理解语法用法。
- `UserCorrection`：用户输入的纠错结果，字段：
  - `original`：原始用户日语。
  - `corrected`：建议修改后的日语句子。
  - `explain`：文字说明，指出错误原因或改进点。
- `TurnResult`：单轮对话统一输出，字段：
  - `jp`：AI 的日文回复。
  - `zh`：将回复翻译成的中文文本。
  - `user_correction`：`UserCorrection` 或 `None`，表示是否进行了纠错。
  - `grammar_ai`：`GrammarPoint` 列表，列出回复中的语法点。
  - `level`：推断的用户当前等级（`None` 表示未跟踪）。

### 5.2 课程类型
- `VocabItem`：课程词汇条目，字段 `jp/reading/zh/example` 分别表示日文、读音、中文释义与例句。
- `GrammarItem`：课程语法条目，字段：
  - `name`：语法点名称。
  - `pattern`：构成规则或公式。
  - `explanation`：中文说明。
  - `examples`：示例句列表。
  - `level`：适用的日语等级。
- `Lesson`：完整课程对象，字段：
  - `id`：课程唯一标识。
  - `title`：课程标题。
  - `level`：课程难度等级。
  - `vocab`：`VocabItem` 数组。
  - `grammar`：`GrammarItem` 数组。

### 5.3 场景类型
- `ScenarioTurn`：场景脚本的一句话，字段 `role`（`system`/`npc`）、`jp`（日语台词）、`zh`（中文释义）。
- `Scenario`：完整场景剧本，字段：
  - `id/title/description/level`：场景元信息。
  - `related_lessons`：关联课程 ID 列表。
  - `script`：`ScenarioTurn` 数组，按顺序排列。

### 5.4 用户状态类型
- `GrammarStats`：语法点练习统计，字段 `seen`（出现次数）与 `wrong`（纠错次数）。
- `UserState`：用户整体学习状态，字段：
  - `user_id`：用户标识。
  - `level`：当前难度等级。
  - `grammar_stats`：`{语法点名: GrammarStats}` 的映射。

## 6. 核心引擎与函数
### 6.1 对话引擎（`core/conversation_engine.py`）
- `process_user_utterance(user_text, history=None, user_id=None) -> TurnResult`：
  - **作用**：封装完整的对话流程，串联纠错 → AI 回复 → 语法识别 → 翻译 → 用户状态写回。
  - **参数**：
    - `user_text`：用户当前日语输入（必填）。
    - `history`：[{`role`, `content`}] 的历史对话，可选；为空时仅用当前句生成回复。
    - `user_id`：用于持久化等级与语法统计的用户 ID，可选。
  - **返回**：`TurnResult`。当 `user_id` 存在时，`level` 字段会被更新后的等级填充。
  - **副作用**：当传入 `user_id` 时，会读取/写入 `data/user_state/{user_id}.json` 并触发等级判断。
- `_analyze_user_sentence(user_text) -> UserCorrection | None`：
  - **作用**：调用 LLM 生成纠错建议；解析首行作为修改后的句子，其余行作为说明。
  - **返回**：`UserCorrection`（包含 `original/corrected/explain`）或在空输出时返回 `None`。
- `_generate_ai_reply(user_text, history) -> str`：
  - **作用**：构造系统提示词与历史消息后调用 `call_llm`，产生日文回复。
  - **历史处理**：遍历 `history` 中的字典，将 `role/content` 依序追加到 prompt。
  - **返回**：去除首尾空白的日文文本；若为空则回退为「すみません、もう一度お願いします。」。
- `_extract_grammar_points(ai_reply) -> List[GrammarPoint]`：
  - **作用**：对 AI 回复文本执行 `detect_grammar`，输出结构化语法点列表。
- `_translate_to_zh(jp_text) -> str`：
  - **作用**：构造翻译提示词调用 `call_llm`，将日语译为中文。
  - **返回**：翻译文本；若 LLM 返回空字符串，则回退为原文。

### 6.2 语法引擎与规则
- `core/grammar_rules.py`
  - `GRAMMAR_PATTERNS`：硬编码语法规则表，元素字段 `name/pattern/description/example`。`pattern` 为字符串列表，只要其中任意片段包含于输入文本，即视为命中并返回对应语法点。
- `core/grammar_engine.py`
  - `detect_grammar(jp_text: str) -> List[GrammarPoint]`：逐条遍历 `GRAMMAR_PATTERNS`，在文本命中时将 `name/description/example` 打包为 `GrammarPoint`。若同一语法的多个关键词存在，只要命中一项即记录一次。

### 6.3 课程引擎（`core/lesson_engine.py` & `core/lesson_models.py`）
- `SAMPLE_LESSONS`：预置的 `Lesson` 列表，提供示例课程数据。
- `get_lesson(lesson_id) -> Lesson | None`：按 ID 全量返回课程；未找到返回 `None`。
- `get_lesson_steps(lesson) -> list[dict]`：
  - 将 `Lesson` 拆解为步骤数组，每个词汇/语法一条，生成字段：`type`（`vocab`/`grammar`）、`index`、`total`、`data`（原始词汇或语法对象）。
  - `total` 为词汇与语法总数；`index` 从 0 递增。
- `get_step(lesson_id, step_index) -> dict`：
  - 统一入口，内部先 `get_lesson`，再 `get_lesson_steps`，最后按索引取结果。
  - 当课程缺失时抛 `ValueError`；索引越界抛 `IndexError`，便于调用方显式捕获。

### 6.4 场景引擎（`core/scenario_engine.py` & `core/scenario_models.py`）
- `SAMPLE_SCENARIOS`：预置的场景剧本列表，含 meta 信息与台词脚本。
- `get_scenario(scenario_id) -> Scenario | None`：按 ID 查询场景。
- `get_step(scenario_id, step_index) -> dict`：
  - 仅返回脚本指定步的 `role/jp/zh/index/total`，输入无效（ID 不存在或越界）时返回空字典。
- `run_step(scenario_id, step_index, user_text) -> dict`：
  - **展示模式**：当 `user_text` 为 `None` 时，直接调用 `get_step` 返回台词而不触发 AI。
  - **对话模式**：当有用户回复时，先执行 `process_user_utterance` 获得纠错/翻译/语法分析，然后尝试取下一条 NPC/system 台词，最终返回 `{npc_line, analysis}`。
  - 输入无效（场景缺失、脚本为空或索引越界）时返回空字典。

### 6.5 用户状态引擎（`core/user_state.py`）
- `DEFAULT_LEVEL = "N5"`：默认起始等级。
- `_get_state_dir() -> Path`：创建并返回 `data/user_state` 目录路径（内部使用）。
- `_get_state_path(user_id) -> Path`：返回用户状态 JSON 路径（内部使用）。
- `load_user_state(user_id) -> UserState`：
  - 如文件缺失，返回默认状态 `{level: N5, grammar_stats: {}}`；否则读取 JSON 并填充缺省值。
- `save_user_state(state) -> None`：把 `UserState` 写入对应 JSON，带缩进与 UTF-8。
- `update_state_with_turn(state, turn) -> UserState`：
  - 遍历 `turn["grammar_ai"]`，对每个语法名累加 `seen`；若 `turn` 包含 `user_correction` 则同步累加 `wrong`。
  - 原地更新并返回传入的 `state` 引用，便于链式调用。
- `_level_up(level) / _level_down(level) -> str`：在预定义等级序列中升/降一级；传入未知等级则回退 `DEFAULT_LEVEL`。
- `decide_next_level(state) -> str`：
  - 基于全局错误率决策：当 `seen_total >= 30` 且错误率 < 0.15 时升一级；当错误率 > 0.5 时降一级；否则保持。
  - 若无统计数据，则直接返回当前等级。
- `apply_level_update(state) -> UserState`：将 `decide_next_level` 结果写回 `state["level"]` 并返回。

### 6.6 LLM 调度（`core/llm_client.py`）
- `LLMConfig`：记录 LLM 调度配置字段：
  - `model_local`（默认 `qwen2.5:7b`）、`model_fallback`（默认 `gpt-4o-mini`）、`timeout`（秒）、`use_fallback`（是否在主模型失败时启用兜底）。
- `call_ollama(messages) -> str`：
  - 校验输入后通过 `tools.ollama_tools.ollama_chat` 调用本地 Ollama；清洗返回文本为空则抛 `RuntimeError`。
- `call_fallback(messages) -> str`：兜底模型占位，当前仅回传固定提示。
- `call_llm(messages) -> str`：
  - 首选 `call_ollama`；若抛出任何异常且 `use_fallback=True`，则调用 `call_fallback`；两者均失败时抛 `RuntimeError`。

### 6.7 其他实用工具
- `core/ruby_utils.py`：`add_ruby(text) -> str` 目前直接回传原文；docstring 提供未来基于“漢字(かな)”的注音替换思路。

## 7. MCP 工具（`tools/`）与入口
### 7.1 工具函数
- `japanese_chat_tools.jp_chat_turn(user_text, history=None, user_id=None) -> dict`：
  - `user_text`：用户日语输入；`history`：[{`role`, `content`}] 对话史，可选；`user_id`：需要记录状态时填写。
  - 异步调用 `process_user_utterance`，返回 `TurnResult`（字典形式）。
- `grammar_tools.jp_detect_grammar(text) -> list[dict]`：
  - `text`：要分析的日语字符串。
  - 直接透传 `detect_grammar`，返回 `GrammarPoint` 字典列表。
- `lesson_tools.get_lesson_overview(lesson_id) -> dict`：
  - `lesson_id`：课程 ID。
  - 返回 `id/title/level/vocab_count/grammar_count`；未找到课程会抛 `ValueError`。
- `lesson_tools.get_lesson_step(lesson_id, step_index) -> dict`：
  - `lesson_id`：课程 ID；`step_index`：步骤索引（从 0 开始）。
  - 调用 `get_step` 返回指定步骤；课程缺失或越界将抛异常。
- `scenario_tools.scenario_get_step(scenario_id, step_index) -> dict`：
  - `scenario_id`：场景 ID；`step_index`：脚本索引。
  - 查询场景某一步，输入无效时返回空字典。
- `scenario_tools.scenario_reply(scenario_id, step_index, user_text) -> dict`：
  - `scenario_id`：场景 ID；`step_index`：当前台词索引；`user_text`：用户的日语回复。
  - 异步调用 `run_step`，返回 `{npc_line, analysis}` 或空字典。
- `user_state_tools.get_user_state(user_id) -> dict`：
  - `user_id`：要读取的用户标识。
  - 加载用户状态（调用 `load_user_state`）。
- `user_state_tools.reset_user_state(user_id) -> dict`：
  - `user_id`：要重置的用户标识。
  - 将等级重置为 `N5`、清空 `grammar_stats` 后持久化并返回。
- `ollama_tools.ollama_chat(model, messages) -> str`：
  - `model`：Ollama 模型名称；`messages`：[{`role`, `content`}] 对话数组。
  - 包装 Ollama SDK 的异步聊天接口；校验参数非空，若无内容则抛 `RuntimeError`。

### 7.2 服务器与应用实例
- `mcp_app.py`：初始化全局 `FastMCP` 实例 `mcp`，名称 `AI_Language_Trainer`，供工具装饰器与服务端共享。
- `server.py`：导入所有工具模块以注册 MCP 工具，并在 `main()` 中调用 `mcp.run()` 启动服务器。

### 7.3 本地 REPL（`repl.py`）
- `call_tool(name, args)` / `call_tool_sync(name, args)`：
  - `name`：要调用的 MCP 工具名；`args`：传入的参数字典。
  - 基于进程内 `fastmcp.Client` 的异步/同步封装，`call_tool_sync` 内部使用 `asyncio.run`。
- `Session`：`dataclass`，字段 `current_user_id`（默认 `default`）与 `history`（当前未用于对话调用）。
- `print_banner()` / `print_help()`：输出欢迎语与命令列表，无参数。
- `format_grammar_stats(grammar_stats)`：
  - `grammar_stats`：形如 `{name: {seen, wrong}}` 的统计字典。
  - 按出现次数排序，返回前 5 条拼接的字符串。
- `print_user_state(state)`：
  - `state`：`UserState` 风格的字典。
  - 打印用户 ID、等级和格式化后的语法统计。
- `handle_command(line, session)`：
  - `line`：用户输入的命令行；`session`：当前 `Session`。
  - 解析 `/...` 命令（用户切换、课程/场景查询、状态查看/重置等）；返回布尔值表示是否继续循环。
- `handle_free_talk(text, session)`：
  - `text`：用户日语输入；`session`：当前 `Session`。
  - 调用 `jp_chat_turn` 进行自由对话，并按区块打印回复/纠错/语法/等级。
- `main()`：REPL 主循环；根据输入选择命令模式或自由对话模式，支持 Ctrl+C/EOF 退出。

## 8. 示例
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

## 9. 项目结构
同「架构概述」所示，可按需要在 `core/` 和 `tools/` 扩展功能。

## 10. 扩展指南
- 新增语法点：在 `core/grammar_rules.py` 中追加 `GRAMMAR_PATTERNS` 项
- 新增课程：在 `core/lesson_models.py` 中扩展 `SAMPLE_LESSONS`，或在 `data/lessons.json` 补充数据
- 扩展场景：在 `core/scenario_models.py` 添加新的 `SAMPLE_SCENARIOS`，脚本可同步写入 `data/scenarios.json`
- 加入更强模型：修改 `core/llm_client.py` 中的 `LLMConfig` 或完善 `call_fallback` 以接入更强大的远程模型

## 11. License (MIT)
本项目使用 MIT License，详见仓库 LICENSE（如无可自行添加）。
