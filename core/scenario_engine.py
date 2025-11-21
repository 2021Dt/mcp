"""提供场景脚本的读取与对话推进逻辑。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.conversation_engine import process_user_utterance
from core.scenario_models import SAMPLE_SCENARIOS, Scenario, ScenarioTurn


def get_scenario(scenario_id: str) -> Optional[Scenario]:
    """根据场景 ID 查找对应的场景定义。"""

    for scenario in SAMPLE_SCENARIOS:
        if scenario["id"] == scenario_id:
            return scenario
    return None


def get_step(scenario_id: str, step_index: int) -> dict:
    """返回指定步骤的台词内容以及进度信息。"""

    scenario = get_scenario(scenario_id)
    if scenario is None:
        return {}

    script = scenario.get("script", [])
    if step_index < 0 or step_index >= len(script):
        return {}

    turn = script[step_index]
    return {
        "role": turn.get("role", ""),
        "jp": turn.get("jp", ""),
        "zh": turn.get("zh", ""),
        "index": step_index,
        "total": len(script),
    }


async def run_step(
    scenario_id: str, step_index: int, user_text: Optional[str]
) -> Dict[str, Any]:
    """执行或推进指定场景步骤，必要时调用对话引擎给出反馈。"""

    scenario = get_scenario(scenario_id)
    if scenario is None:
        return {}

    script = scenario.get("script", [])
    if not script or step_index < 0 or step_index >= len(script):
        return {}

    # 展示模式：直接返回脚本内容
    if user_text is None:
        return get_step(scenario_id, step_index)

    # 用户回复后，先调用对话引擎生成纠错与语法等分析
    analysis = await process_user_utterance(user_text)

    # 尝试拿到下一条 NPC 或 system 台词
    next_turn: Optional[ScenarioTurn] = None
    next_index = step_index + 1
    if next_index < len(script):
        next_turn = script[next_index]

    npc_payload: Optional[dict] = None
    if next_turn:
        npc_payload = {
            "role": next_turn.get("role", ""),
            "jp": next_turn.get("jp", ""),
            "zh": next_turn.get("zh", ""),
            "index": next_index,
            "total": len(script),
        }

    return {
        "npc_line": npc_payload,
        "analysis": analysis,
    }
