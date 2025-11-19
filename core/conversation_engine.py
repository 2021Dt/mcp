"""负责 AI 日语陪练核心对话流程的算法骨架。"""

from __future__ import annotations

from typing import List, Optional, TypedDict

from core.llm_client import call_llm


class GrammarPoint(TypedDict):
    """表示 AI 回复中涉及的语法点结构。"""

    name: str
    description: str
    example: str


class UserCorrection(TypedDict):
    """记录对用户发言的纠错信息。"""

    original: str
    corrected: str
    explain: str


class TurnResult(TypedDict):
    """封装单轮对话的最终输出。"""

    jp: str
    zh: str
    user_correction: Optional[UserCorrection]
    grammar_ai: List[GrammarPoint]


async def process_user_utterance(
    user_text: str, history: Optional[list[dict]] = None
) -> TurnResult:
    """完成一次用户输入到 AI 输出的对话轮次（异步版本）。

    参数：
        user_text: 用户输入的原始日语句子。
        history: 先前的对话历史（可空），结构在未来由会话管理器定义。

    返回：
        TurnResult: 包含 AI 回复（日文+注音）、中文翻译、纠错信息以及语法点列表。

    当前实现仅拼装占位数据，未来可在各私有函数中接入真实模型、提示词与
    检索逻辑。该函数作为对外统一入口，保持签名稳定以便调用方集成。
    """

    correction = await _analyze_user_sentence(user_text)
    ai_reply = await _generate_ai_reply(user_text, history)
    grammar_points = await _extract_grammar_points(ai_reply)
    zh_translation = await _translate_to_zh(ai_reply)

    return TurnResult(
        jp=ai_reply,
        zh=zh_translation,
        user_correction=correction,
        grammar_ai=grammar_points,
    )


async def _analyze_user_sentence(user_text: str) -> Optional[UserCorrection]:
    """调用 LLM 生成纠错意见，并包装为 `UserCorrection`。"""

    messages = [
        {
            "role": "system",
            "content": "你是一名日语老师，请给出纠错建议并解释原因。",
        },
        {
            "role": "user",
            "content": f"请帮我纠正以下日文句子并解释：{user_text}",
        },
    ]
    suggestion = await call_llm(messages)
    stripped = suggestion.strip()
    if not stripped:
        return None
    return UserCorrection(original=user_text, corrected=user_text, explain=stripped)


async def _generate_ai_reply(user_text: str, history: Optional[list[dict]]) -> str:
    """构造 OpenAI 风格消息并调用统一 LLM 生成日文回复。"""

    system_prompt = "你是一名温柔的日语会话老师，请使用自然日语并在合适处加入注音。"
    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    if history:
        for turn in history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_text})
    reply = await call_llm(messages)
    return reply.strip() or "TODO: 生成 AI 回复"


async def _extract_grammar_points(ai_reply: str) -> List[GrammarPoint]:
    """语法点提取仍保持占位，暂不调用模型。"""

    _ = ai_reply
    return []


async def _translate_to_zh(jp_text: str) -> str:
    """使用 LLM 进行简单的日文到中文翻译。"""

    messages = [
        {"role": "system", "content": "你是专业的日文翻译，请输出中文释义。"},
        {"role": "user", "content": f"请把下面的日文翻成中文：{jp_text}"},
    ]
    translation = await call_llm(messages)
    return translation.strip() or "TODO: 中文翻译"
