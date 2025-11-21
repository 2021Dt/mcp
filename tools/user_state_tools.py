"""用户状态读写工具层。"""

from mcp_app import mcp
from core.engines.user_state_engine import load_user_state, save_user_state


@mcp.tool()
def get_user_state(user_id: str) -> dict:
    """读取指定用户的学习状态。"""

    return load_user_state(user_id)


@mcp.tool()
def reset_user_state(user_id: str) -> dict:
    """重置指定用户的学习状态。"""

    state = load_user_state(user_id)
    state["grammar_stats"] = {}
    state["level"] = "N5"
    save_user_state(state)
    return state
