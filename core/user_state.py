"""负责管理用户学习状态（语法点熟练度与等级）的引擎模块。"""

from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, TypedDict

from core.conversation_engine import TurnResult

# --- 数据结构 ---


class GrammarStats(TypedDict):
    """记录单个语法点的学习数据。"""

    seen: int
    wrong: int


class UserState(TypedDict):
    """整体的用户学习状态。"""

    user_id: str
    level: str
    grammar_stats: Dict[str, GrammarStats]


# --- 配置 ---

DEFAULT_LEVEL = "N5"


# --- 路径工具 ---


def _get_state_dir() -> Path:
    """返回存放用户状态 JSON 的目录路径，若不存在则自动创建。"""

    state_dir = Path("data") / "user_state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def _get_state_path(user_id: str) -> Path:
    """返回某个用户对应的 JSON 状态文件路径。"""

    return _get_state_dir() / f"{user_id}.json"


# --- 核心 API ---


def load_user_state(user_id: str) -> UserState:
    """加载用户状态；若文件不存在则返回默认状态。"""

    path = _get_state_path(user_id)
    if not path.exists():
        return UserState(
            user_id=user_id,
            level=DEFAULT_LEVEL,
            grammar_stats={},
        )

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    level = data.get("level", DEFAULT_LEVEL)
    grammar_stats = data.get("grammar_stats", {})

    return UserState(user_id=user_id, level=level, grammar_stats=grammar_stats)


def save_user_state(state: UserState) -> None:
    """将用户状态保存为 JSON 文件。"""

    path = _get_state_path(state["user_id"])
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# --- 状态更新逻辑 ---


def update_state_with_turn(state: UserState, turn: TurnResult) -> UserState:
    """根据对话结果更新语法统计信息。"""

    grammar_stats = state.setdefault("grammar_stats", {})

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


# --- 等级决策 ---


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
