"""负责管理用户学习状态（语法点熟练度与等级）的引擎模块。"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from core.models import GrammarStats, TurnResult, UserState
from core.utils.dp_log import LogFactory
from core.utils.helpers import dump_json, load_json

logger = LogFactory.get_logger(__name__)

DEFAULT_LEVEL = "N5"
_STATE_DIR = Path("data") / "user_state"


def _get_state_path(user_id: str) -> Path:
    """返回某个用户对应的 JSON 状态文件路径。"""

    return _STATE_DIR / f"{user_id}.json"


def load_user_state(user_id: str) -> UserState:
    """加载用户状态；若文件不存在则返回默认状态。"""

    path = _get_state_path(user_id)
    data = load_json(
        path,
        {
            "user_id": user_id,
            "level": DEFAULT_LEVEL,
            "grammar_stats": {},
        },
    )
    logger.debug(f"load_user_state for {user_id}")
    return UserState(
        user_id=data.get("user_id", user_id),
        level=data.get("level", DEFAULT_LEVEL),
        grammar_stats=data.get("grammar_stats", {}),
    )


def save_user_state(state: UserState) -> None:
    """将用户状态保存为 JSON 文件。"""

    path = _get_state_path(state["user_id"])
    dump_json(path, state)
    logger.debug(f"save_user_state for {state.get('user_id')}")


def update_state_with_turn(state: UserState, turn: "TurnResult") -> UserState:
    """根据对话结果更新语法统计信息。"""

    grammar_stats: Dict[str, GrammarStats] = state.setdefault("grammar_stats", {})

    for grammar in turn.get("grammar_ai", []):
        name = grammar.get("name", "").strip()
        if not name:
            continue
        stats = grammar_stats.setdefault(name, {"seen": 0, "wrong": 0})
        stats["seen"] += 1
        if turn.get("user_correction") is not None:
            stats["wrong"] += 1

    state["grammar_stats"] = grammar_stats
    return state


_LEVEL_ORDER = ["N5", "N4", "N3", "N2", "N1"]


def _level_up(level: str) -> str:
    """在预定义顺序中提升一级。"""

    try:
        idx = _LEVEL_ORDER.index(level)
    except ValueError:
        return DEFAULT_LEVEL
    return _LEVEL_ORDER[min(idx + 1, len(_LEVEL_ORDER) - 1)]


def _level_down(level: str) -> str:
    """在预定义顺序中下降一级。"""

    try:
        idx = _LEVEL_ORDER.index(level)
    except ValueError:
        return DEFAULT_LEVEL
    return _LEVEL_ORDER[max(idx - 1, 0)]


def decide_next_level(state: UserState) -> str:
    """基于总体错误率简单决定下一阶段等级。"""

    grammar_stats = state.get("grammar_stats", {})
    seen_total = sum(item.get("seen", 0) for item in grammar_stats.values())
    wrong_total = sum(item.get("wrong", 0) for item in grammar_stats.values())

    if seen_total == 0:
        return state.get("level", DEFAULT_LEVEL)

    error_rate = wrong_total / seen_total
    current_level = state.get("level", DEFAULT_LEVEL)

    if seen_total >= 30 and error_rate < 0.15:
        return _level_up(current_level)
    if seen_total >= 30 and error_rate > 0.5:
        return _level_down(current_level)
    return current_level


def apply_level_update(state: UserState) -> UserState:
    """根据决策结果更新用户等级并返回新状态。"""

    next_level = decide_next_level(state)
    state["level"] = next_level
    return state
