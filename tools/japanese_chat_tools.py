"""日语聊天相关工具占位实现。"""

from mcp_app import mcp


@mcp.tool()
async def jp_chat_turn(user_text: str, history: list[dict] | None = None) -> dict:
    """调用异步核心引擎处理单轮对话。"""

    from core.conversation_engine import process_user_utterance

    result = await process_user_utterance(user_text, history)
    return result
