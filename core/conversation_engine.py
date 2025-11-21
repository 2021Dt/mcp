"""负责 AI 日语陪练核心对话流程的算法骨架。"""

from __future__ import annotations

from typing import List, Optional, TypedDict

from core.llm_client import call_llm
from core.grammar_engine import detect_grammar
from core.user_state import (
    apply_level_update,
    load_user_state,
    save_user_state,
    update_state_with_turn,
)


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
    level: Optional[str]


async def process_user_utterance(
    user_text: str,
    history: Optional[list[dict]] = None,
    user_id: str | None = None,
) -> TurnResult:
    """完成一次用户输入到 AI 输出的对话轮次（异步版本）。"""

    correction = await _analyze_user_sentence(user_text)
    ai_reply = await _generate_ai_reply(user_text, history)
    grammar_points = await _extract_grammar_points(ai_reply)
    zh_translation = await _translate_to_zh(ai_reply)
    turn_result: TurnResult = TurnResult(
        jp=ai_reply,
        zh=zh_translation,
        user_correction=correction,
        grammar_ai=grammar_points,
        level=None,
    )

    if user_id:
        state = load_user_state(user_id)
        state = update_state_with_turn(state, turn_result)
        state = apply_level_update(state)
        save_user_state(state)
        turn_result["level"] = state.get("level")

    return turn_result


async def _analyze_user_sentence(user_text: str) -> Optional[UserCorrection]:
    """调用 LLM 生成纠错意见，并包装为 `UserCorrection`。"""

    messages = [
        {
            "role": "system",
            "content": "你是一名严格的日语老师，请指出语法与用词问题。",
        },
        {
            "role": "user",
            "content": f"请纠正这个日语句子并解释错误：{user_text}",
        },
    ]
    suggestion = await call_llm(messages)
    stripped = suggestion.strip()
    if not stripped:
        return None

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if not lines:
        return None

    corrected_line = lines[0]
    _, _, corrected_after = corrected_line.partition(":")
    corrected_text = corrected_after.strip() or corrected_line
    explanation = "\n".join(lines[1:]).strip() if len(lines) > 1 else corrected_line

    return UserCorrection(
        original=user_text,
        corrected=corrected_text or user_text,
        explain=explanation or stripped,
    )


async def _generate_ai_reply(user_text: str, history: Optional[list[dict]]) -> str:
    """构造消息后调用统一 LLM 生成日文回复。"""

    messages: list[dict] = [
        {
            "role": "system",
            "content": "你是一位友好的日语对话伙伴，请保持自然且鼓励式的语气。",
        }
    ]
    if history:
        for turn in history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if not content:
                continue
            messages.append({"role": role, "content": content})
    messages.append(
        {
            "role": "user",
            "content": f"你是一个日语对话伙伴，请用自然日语回复：{user_text}",
        }
    )
    reply = await call_llm(messages)
    return reply.strip() or "すみません、もう一度お願いします。"


async def _extract_grammar_points(ai_reply: str) -> List[GrammarPoint]:
    """调用语法引擎对 AI 回复进行语法点识别。"""

    return detect_grammar(ai_reply)


async def _translate_to_zh(jp_text: str) -> str:
    """使用 LLM 进行简单的日文到中文翻译。"""

    messages = [
        {"role": "system", "content": "你是一名专业的中日互译译者。"},
        {"role": "user", "content": f"请把以下日语翻译成中文：{jp_text}"},
    ]
    translation = await call_llm(messages)
    return translation.strip() or jp_text
