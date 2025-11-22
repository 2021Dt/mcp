"""命令行持续会话式 REPL 客户端，便于直接调用 AI 日语陪练系统。"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List
import json

from fastmcp import Client
from fastmcp.client.client import CallToolResult

from core.services.agent_runner import AgentRunner
from core.services.ai_client import AIClient
from mcp_app import mcp

# ⚠️ 必须导入所有工具模块以触发 @mcp.tool 注册
import tools.japanese_chat_tools  # noqa: F401
import tools.lesson_tools  # noqa: F401
import tools.scenario_tools  # noqa: F401
import tools.user_state_tools  # noqa: F401
import tools.grammar_tools  # noqa: F401
import tools.ollama_tools  # noqa: F401

mcp_client = Client(mcp)
ai_client = AIClient()
agent_runner = AgentRunner(ai_client, mcp_client)


async def call_tool(name: str, args: Dict[str, Any]) -> Any:
    """以异步方式调用 MCP 工具，使用进程内 FastMCP 客户端。"""

    async with mcp_client:
        return await mcp_client.call_tool(name, args)


def call_tool_sync(name: str, args: Dict[str, Any]) -> Any:
    """同步封装，便于在 REPL 中直接调用工具。"""

    return extract_state_dict(asyncio.run(call_tool(name, args)))


@dataclass
class Session:
    """维护当前 REPL 会话状态。"""

    current_user_id: str = "default"
    history: List[Dict[str, Any]] = field(default_factory=list)

    def set_user(self, user_id: str) -> None:
        """切换当前用户 ID。"""

        self.current_user_id = user_id


def print_banner() -> None:
    """打印欢迎信息。"""

    print("=" * 28)
    print("  AI 日语陪练 REPL")
    print("=" * 28)
    print("命令：/help 查看帮助，/exit 退出")
    print("当前用户: default")
    print("-" * 32)


def print_help() -> None:
    """输出所有可用命令说明。"""

    print("可用命令：")
    print("  /help                          查看帮助")
    print("  /exit                          退出 REPL")
    print("  /user <user_id>                切换当前用户 ID")
    print("  /state                         查看当前用户状态")
    print("  /state reset                   重置当前用户状态")  # 这里可以搞成可选参数。
    print("  /lesson <lesson_id>            查看课程概览")
    print("  /lesson-step <lesson_id> <i>   查看课程某一步")
    print("  /scenario <scene_id> <i>       查看场景某一步台词")
    print("  /scenario-reply <scene_id> <i> <日文回复>  回应场景并查看分析")
    print("  普通文本                       进入自由对话模式（AgentRunner 驱动）")


def format_grammar_stats(grammar_stats: Dict[str, Dict[str, int]]) -> str:
    """将语法统计信息格式化成可读文本，仅显示 Top 5。"""

    if not grammar_stats:
        return "(暂无语法统计)"

    sorted_items = sorted(
        grammar_stats.items(),
        key=lambda item: item[1].get("seen", 0),
        reverse=True,
    )
    lines = []
    for name, stats in sorted_items[:5]:
        seen = stats.get("seen", 0)
        wrong = stats.get("wrong", 0)
        lines.append(f"- {name}: seen={seen}, wrong={wrong}")
    return "\n".join(lines)


def extract_state_dict(state: Any) -> Dict[str, Any]:
    """
    将输入转成 dict。
    自动判断是普通 dict 还是 MCP CallToolResult。
    """

    # ① 如果本来就是 dict，直接返回
    if isinstance(state, dict):
        return state

    # ② 如果是 CallToolResult：从 content 中解析 JSON 文本
    if isinstance(state, CallToolResult):
        if not state.content:
            raise ValueError("CallToolResult.content 为空，无法解析用户状态")

        content_item = state.content[0]

        # content_item 必须是 TextContent
        text = getattr(content_item, "text", None)
        if not text:
            raise ValueError("CallToolResult.content 第0项没有 text 字段")

        try:
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"无法解析 JSON：{e}")

    raise TypeError(f"无法处理的 state 类型: {type(state)}")


def print_user_state(state: dict) -> None:
    """人类可读输出用户状态（兼容 dict / CallToolResult）"""

    user_id = state.get("user_id", "?")
    level = state.get("level", "?")
    grammar_stats = state.get("grammar_stats", {})

    print(f"用户: {user_id}")
    print(f"当前等级: {level}")
    print("语法统计 Top 5:")
    print(format_grammar_stats(grammar_stats))


def handle_command(line: str, session: Session) -> bool:
    """解析并处理以 / 开头的命令，返回 False 表示退出。"""

    parts = line.strip().split()
    if not parts:
        return True
    cmd = parts[0].lower()

    try:
        if cmd == "/help":
            print_help()
        elif cmd == "/exit":
            print("再见，欢迎下次继续练习！")
            return False
        elif cmd == "/user":
            if len(parts) < 2:
                print("[用法] /user <user_id>")
            else:
                session.set_user(parts[1])
                print(f"已切换当前用户为: {session.current_user_id}")  # 这里后面做权限管理
        elif cmd == "/state":
            if len(parts) >= 2 and parts[1].lower() == "reset":
                state = call_tool_sync(
                    "reset_user_state", {"user_id": session.current_user_id}
                )
                print("已重置当前用户状态。")
                print_user_state(state)
            else:
                state = call_tool_sync(
                    "get_user_state", {"user_id": session.current_user_id}
                )
                print_user_state(state)
        elif cmd == "/lesson":
            if len(parts) < 2:
                print("[用法] /lesson <lesson_id>")
            else:
                overview = call_tool_sync(
                    "get_lesson_overview", {"lesson_id": parts[1]}
                )
                if overview:
                    print("课程概览：")
                    print(
                        f"- 标题: {overview.get('title')} (ID: {overview.get('id')}, 等级: {overview.get('level')})"
                    )
                    print(
                        f"- 词汇数: {overview.get('vocab_count')} / 语法点数: {overview.get('grammar_count')}"
                    )
                else:
                    print(f'当前无课程lesson {parts[1]} 的相关信息，请检查课程信息是否注册。')
        elif cmd == "/lesson-step":
            if len(parts) < 3:
                print("[用法] /lesson-step <lesson_id> <step_index>")
            else:
                try:
                    step_index = int(parts[2])
                except ValueError:
                    print("[错误] step_index 需要是整数。")
                    return True
                step = call_tool_sync(
                    "get_lesson_step",
                    {"lesson_id": parts[1], "step_index": step_index},
                )
                print(f"课程步骤 {step.get('index')} / {step.get('total')}：")
                print(f"- 类型: {step.get('type')}")
                print(f"- 数据: {step.get('data')}")
        elif cmd == "/scenario":
            if len(parts) < 3:
                print("[用法] /scenario <scenario_id> <step_index>")
            else:
                try:
                    step_index = int(parts[2])
                except ValueError:
                    print("[错误] step_index 需要是整数。")
                    return True
                step = call_tool_sync(
                    "scenario_get_step",
                    {"scenario_id": parts[1], "step_index": step_index},
                )
                if step:
                    print(f"场景步骤 {step.get('index')} / {step.get('total')}：")
                    print(f"- 角色: {step.get('role')}")
                    print(f"- 日语: {step.get('jp')}")
                    print(f"- 中文: {step.get('zh')}")
                else:
                    print(f'当前无场景步骤 {parts[1]} 的相关信息，请检查相关场景是否注册。')
        elif cmd == "/scenario-reply":
            if len(parts) < 4:
                print("[用法] /scenario-reply <scenario_id> <step_index> <日文回复>")
            else:
                try:
                    step_index = int(parts[2])
                except ValueError:
                    print("[错误] step_index 需要是整数。")
                    return True
                reply_text = " ".join(parts[3:])
                result = call_tool_sync(
                    "scenario_reply",
                    {
                        "scenario_id": parts[1],
                        "step_index": step_index,
                        "user_text": reply_text,
                    },
                )
                npc_line = result.get("npc_line")
                analysis = result.get("analysis")
                print("NPC 下一句：")
                if npc_line:
                    print(f"- 日语: {npc_line.get('jp')}")
                    print(f"- 中文: {npc_line.get('zh')}")
                print("用户回复分析：")
                if analysis:
                    print(f"[AI 日语] {analysis.get('jp')}")
                    print(f"[中文] {analysis.get('zh')}")
                    correction = analysis.get("user_correction")
                    if correction:
                        print("[纠错]")
                        print(f"- 原句: {correction.get('original')}")
                        print(f"- 修改: {correction.get('corrected')}")
                        print(f"- 说明: {correction.get('explain')}")
                    grammar_list = analysis.get("grammar_ai") or []
                    if grammar_list:
                        print("[语法]")
                        for g in grammar_list:
                            print(f"- {g.get('name')}: {g.get('description')}")
                    if analysis.get("level"):
                        print(f"[当前等级] {analysis.get('level')}")
                else:
                    print("(无分析结果)")
        else:
            print("[错误] 未知命令，输入 /help 查看用法。")
    except Exception as exc:  # noqa: BLE001
        print(f"[错误] 调用工具 {cmd} 失败：{exc}")

    return True


def handle_free_talk(text: str) -> None:
    """处理自由对话输入，通过 AgentRunner 调度 AI 与工具。"""

    try:
        result = asyncio.run(agent_runner.run(text))
    except Exception as exc:  # noqa: BLE001
        print(f"[错误] 调用 AgentRunner 失败：{exc}")
        return

    print("\n[AgentRunner]")
    print(result)


def main() -> None:
    """启动 REPL 主循环。"""

    print_banner()
    session = Session()

    while True:
        try:
            line = input("[JP-AI] > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见，欢迎下次继续练习！")
            break

        if not line:
            continue

        if line.startswith("/"):
            if not handle_command(line, session):
                break
        else:
            handle_free_talk(line)


if __name__ == "__main__":
    main()
