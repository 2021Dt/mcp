"""场景对话相关工具层。"""

from mcp_app import mcp
from core.engines.scenario_engine import get_step, run_step


@mcp.tool()
def scenario_get_step(scenario_id: str, step_index: int) -> dict:
    """查看场景脚本中的指定步骤。"""

    return get_step(scenario_id, step_index)


@mcp.tool()
async def scenario_reply(
    scenario_id: str, step_index: int, user_text: str
) -> dict:
    """用户回复场景后获取 NPC 下一句以及对回复的分析。"""

    return await run_step(scenario_id, step_index, user_text)
