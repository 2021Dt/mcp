from __future__ import annotations

from typing import Any, List, Optional

from mcp_app import mcp
from core.services.ai_client import AIClient


@mcp.tool()
async def ollama_chat(
    model: str, messages: List[dict[str, Any]], tools: Optional[List[dict]] = None
) -> dict:
    """调用统一 AI 客户端的 Ollama 模式。"""

    client = AIClient(mode="ollama", model=model)
    return await client.chat(messages, tools=tools)
