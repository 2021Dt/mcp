"""集中定义 AI 日语陪练系统的核心数据模型。"""

from typing import TypedDict, List, Optional, Dict

# -----------------------------
# Conversation / Grammar Models
# -----------------------------
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


# -----------------------------
# Lesson Models
# -----------------------------
class VocabItem(TypedDict):
    """课程中的单词条目。"""

    jp: str
    reading: str
    zh: str
    example: str


class GrammarItem(TypedDict):
    """课程中的语法点条目。"""

    name: str
    pattern: str
    explanation: str
    examples: List[str]
    level: str


class Lesson(TypedDict):
    """表示完整课程的结构。"""

    id: str
    title: str
    level: str
    vocab: List[VocabItem]
    grammar: List[GrammarItem]


# -----------------------------
# Scenario Models
# -----------------------------
class ScenarioTurn(TypedDict):
    """场景脚本中的一条台词。"""

    role: str
    jp: str
    zh: str


class Scenario(TypedDict):
    """场景剧本结构。"""

    id: str
    title: str
    description: str
    level: str
    related_lessons: List[str]
    script: List[ScenarioTurn]


# -----------------------------
# User State Models
# -----------------------------
class GrammarStats(TypedDict):
    """记录某语法点的练习统计。"""

    seen: int
    wrong: int


class UserState(TypedDict):
    """记录用户整体学习状态。"""

    user_id: str
    level: str
    grammar_stats: Dict[str, GrammarStats]
