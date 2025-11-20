"""统一的 LLM 调度模块，支持本地 Ollama 与兜底模型。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LLMConfig:
    """描述本地与兜底模型的最小配置集合。"""

    model_local: str = "qwen2.5:7b"
    model_fallback: str = "gpt-4o-mini"
    timeout: int = 30
    use_fallback: bool = True


llm_config = LLMConfig()


async def call_ollama(messages: list[dict[str, Any]]) -> str:
    """通过 MCP 注册的 Ollama 工具执行非流式推理。"""

    if not messages:
        raise ValueError("messages 不能为空")

    try:
        from tools.ollama_tools import ollama_chat
    except ImportError as exc:  # pragma: no cover - 依赖项目结构
        raise RuntimeError("未找到 Ollama 工具，请确认 tools.ollama_tools 可用") from exc

    content = await ollama_chat(llm_config.model_local, messages)
    cleaned = content.strip()
    if not cleaned:
        raise RuntimeError("Ollama 工具返回空文本")
    return cleaned


async def call_fallback(messages: list[dict[str, Any]]) -> str:
    """兜底模型调用的简易占位实现。"""

    _ = messages
    return "fallback: 兜底模型尚未配置"


async def call_llm(messages: list[dict[str, Any]]) -> str:
    """按优先级调用 LLM，如有需要执行兜底逻辑。"""

    try:
        return await call_ollama(messages)
    except Exception:  # noqa: BLE001 - 需要捕获所有异常
        if not llm_config.use_fallback:
            raise
        try:
            fallback_result = await call_fallback(messages)
        except Exception as fallback_exc:  # noqa: BLE001
            raise RuntimeError("本地与兜底模型均调用失败") from fallback_exc
        return fallback_result or "fallback: 返回为空"
