"""场景工具占位模块。"""

from mcp_app import mcp


@mcp.tool()
def scenario_step(scenario_id: str, step: int = 1) -> dict:
    """占位场景工具，返回场景与步骤信息。"""
    return {"scenario_id": scenario_id, "step": step, "status": "占位"}
