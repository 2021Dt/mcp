"""用户学习状态相关的 MCP 工具。"""

from mcp_app import mcp
from core.user_state import load_user_state, save_user_state


@mcp.tool()
def get_user_state(user_id: str) -> dict:
    """获取指定用户的学习状态。"""

    return load_user_state(user_id)


@mcp.tool()
def reset_user_state(user_id: str) -> dict:
    """重置指定用户的学习状态为默认值。"""

    state = load_user_state(user_id)
    state["level"] = "N5"
    state["grammar_stats"] = {}
    save_user_state(state)
    return state
