from typing import Any, Dict, List, Optional

from core.engines.conversation_engine import process_user_utterance
from core.models import Scenario, ScenarioTurn
from core.utils.dp_log import LogFactory

logger = LogFactory.get_logger(__name__)

SAMPLE_SCENARIOS: List[Scenario] = [
    {
        "id": "scene_conbini_01",
        "title": "在便利店购物",
        "description": "练习在便利店购物时的基本对话与礼貌表达。",
        "level": "N5",
        "related_lessons": ["n5_lesson_01"],
        "script": [
            {"role": "system", "jp": "コンビニに入りました。", "zh": "你走进了一家便利店。"},
            {"role": "npc", "jp": "いらっしゃいませ！", "zh": "欢迎光临！"},
            {"role": "system", "jp": "商品を手に取りました。", "zh": "你拿起了想买的商品。"},
            {"role": "npc", "jp": "温めますか？", "zh": "需要加热吗？"},
            {"role": "system", "jp": "レジに並んでいます。", "zh": "你正排队结账。"},
            {"role": "npc", "jp": "ポイントカードはお持ちですか？", "zh": "有积分卡吗？"},
        ],
    }
]


def get_scenario(scenario_id: str) -> Optional[Scenario]:
    """根据场景 ID 查找对应的场景定义。"""

    for scenario in SAMPLE_SCENARIOS:
        if scenario["id"] == scenario_id:
            return scenario
    logger.warning(f"scenario not found: {scenario_id}")
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

    if user_text is None:
        return get_step(scenario_id, step_index)

    analysis = await process_user_utterance(user_text)

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
