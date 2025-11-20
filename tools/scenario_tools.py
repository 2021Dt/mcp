"""场景相关的 MCP 工具，提供步骤查询与回复分析。"""

from mcp_app import mcp
from core.scenario_engine import get_step, run_step


@mcp.tool()
def scenario_get_step(scenario_id: str, step_index: int) -> dict:
    """获取场景指定步骤的内容（不调用 AI 推理）。"""

    return get_step(scenario_id, step_index)


@mcp.tool()
async def scenario_reply(scenario_id: str, step_index: int, user_text: str) -> dict:
    """用户在某场景步骤的回复，返回 AI 分析与下一条台词。"""

    return await run_step(scenario_id, step_index, user_text)
