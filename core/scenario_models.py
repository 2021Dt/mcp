"""定义场景脚本的数据结构与示例场景。"""

from typing import List, TypedDict


class ScenarioTurn(TypedDict):
    """表示场景脚本中的单条台词。"""

    role: str  # "npc" | "system"
    jp: str
    zh: str


class Scenario(TypedDict):
    """表示完整的场景脚本。"""

    id: str
    title: str
    description: str
    level: str
    related_lessons: List[str]
    script: List[ScenarioTurn]


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
