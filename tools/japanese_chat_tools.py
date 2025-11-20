"""日语聊天相关工具占位实现。"""

from mcp_app import mcp


@mcp.tool()
async def jp_chat_turn(
    user_text: str,
    history: list[dict] | None = None,
    user_id: str | None = None,
) -> dict:
    """调用异步核心引擎处理单轮对话并记录学习状态。"""

    from core.conversation_engine import process_user_utterance

    result = await process_user_utterance(
        user_text=user_text,
        history=history,
        user_id=user_id,
    )
    return result
