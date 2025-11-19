"""日语聊天相关工具占位实现。"""

from mcp_app import mcp


@mcp.tool()
def jp_chat_turn(user_text: str) -> dict:
    """占位聊天工具，简单回显用户输入。"""
    return {"echo": user_text}
