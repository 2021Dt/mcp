"""统一的 LLM 调用与降级策略模块。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMConfig:
    """描述本地与兜底模型的最小配置集合。"""

    model_local: str = "qwen2.5:7b"
    model_fallback: str = "gpt-4o-mini"
    timeout: int = 30
    use_fallback: bool = True


llm_config = LLMConfig()


async def call_ollama(messages: list[dict]) -> str:
    """调用本地 Ollama MCP 工具的占位实现。"""

    _ = messages
    return "TODO: 模拟 Ollama 回复"


async def call_fallback(messages: list[dict]) -> str:
    """调用 OpenAI/GPT 类工具的占位实现。"""

    _ = messages
    return "TODO: 模拟 GPT 回复"


async def call_llm(messages: list[dict]) -> str:
    """执行主调度，失败时根据配置选择是否兜底。"""

    try:
        response = await call_ollama(messages)
    except Exception:  # noqa: BLE001 - 需要捕获所有异常以实现兜底
        if not llm_config.use_fallback:
            raise
        try:
            response = await call_fallback(messages)
        except Exception as fallback_exc:  # noqa: BLE001
            raise RuntimeError("本地与兜底模型均调用失败") from fallback_exc
    return response.strip() or "TODO: 空响应"

