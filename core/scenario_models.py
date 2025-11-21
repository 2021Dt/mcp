"""定义场景脚本的数据结构与示例场景。"""

from typing import List

from core.models import Scenario, ScenarioTurn


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
