from typing import TypedDict, List, Optional, Dict

# ------------- Conversation -------------
class GrammarPoint(TypedDict):
    name: str
    description: str
    example: str

class UserCorrection(TypedDict):
    original: str
    corrected: str
    explain: str

class TurnResult(TypedDict):
    jp: str
    zh: str
    user_correction: Optional[UserCorrection]
    grammar_ai: List[GrammarPoint]
    level: Optional[str]

# ------------- Lesson -------------------
class VocabItem(TypedDict):
    jp: str
    reading: str
    zh: str
    example: str

class GrammarItem(TypedDict):
    name: str
    pattern: str
    explanation: str
    examples: List[str]
    level: str

class Lesson(TypedDict):
    id: str
    title: str
    level: str
    vocab: List[VocabItem]
    grammar: List[GrammarItem]

# ------------- Scenario -----------------
class ScenarioTurn(TypedDict):
    role: str
    jp: str
    zh: str

class Scenario(TypedDict):
    id: str
    title: str
    description: str
    level: str
    related_lessons: List[str]
    script: List[ScenarioTurn]

# ------------- User State ---------------
class GrammarStats(TypedDict):
    seen: int
    wrong: int

class UserState(TypedDict):
    user_id: str
    level: str
    grammar_stats: Dict[str, GrammarStats]
