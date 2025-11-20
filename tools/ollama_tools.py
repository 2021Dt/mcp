"""Ollama 相关的 MCP 工具实现。"""

from __future__ import annotations

import logging
from typing import Any

import ollama

from mcp_app import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def ollama_chat(model: str, messages: list[dict[str, Any]]) -> str:
    """调用 Ollama 的非流式接口并返回文本结果。"""

    if not model:
        raise ValueError("model 参数不能为空")
    if not messages:
        raise ValueError("messages 参数不能为空")

    response = await ollama.chat(model=model, messages=messages)
    content = response.get("message", {}).get("content", "")
    if not content:
        logger.warning("Ollama 未返回内容: %s", response)
        raise RuntimeError("Ollama 返回内容为空")
    return content
