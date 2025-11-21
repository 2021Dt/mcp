"""课程分步教学引擎。"""

from typing import Any, Dict, List, Optional

from core.models import GrammarItem, Lesson, VocabItem
from core.utils.dp_log import LogFactory

logger = LogFactory.get_logger(__name__)

SAMPLE_LESSONS: List[Lesson] = [
    {
        "id": "n5_lesson_01",
        "title": "自我介绍入门",
        "level": "N5",
        "vocab": [
            {
                "jp": "はじめまして",
                "reading": "はじめまして",
                "zh": "初次见面",
                "example": "はじめまして、山田です。",
            },
            {
                "jp": "よろしくお願いします",
                "reading": "よろしくおねがいします",
                "zh": "请多关照",
                "example": "これからよろしくお願いします。",
            },
            {
                "jp": "学生",
                "reading": "がくせい",
                "zh": "学生",
                "example": "私は学生です。",
            },
            {
                "jp": "会社員",
                "reading": "かいしゃいん",
                "zh": "公司职员",
                "example": "父は会社員です。",
            },
        ],
        "grammar": [
            {
                "name": "～です",
                "pattern": "名词 + です",
                "explanation": "表示判断或说明，礼貌体。",
                "examples": ["私は学生です。", "田中さんは会社員です。"],
                "level": "N5",
            },
            {
                "name": "～は～です",
                "pattern": "名词1 は 名词2 です",
                "explanation": "提示主题并进行说明。",
                "examples": ["私は山田です。", "これは本です。"],
                "level": "N5",
            },
            {
                "name": "～も",
                "pattern": "名词 も",
                "explanation": "表示“也”，与前项并列。",
                "examples": ["私も学生です。", "彼も日本人です。"],
                "level": "N5",
            },
        ],
    }
]


def get_lesson(lesson_id: str) -> Optional[Lesson]:
    """根据 lesson_id 查找 Lesson。"""

    for lesson in SAMPLE_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    logger.warning(f"lesson not found: {lesson_id}")
    return None


def get_lesson_steps(lesson: Lesson) -> list[dict]:
    """
    将 Lesson 拆成步骤：
    - vocab 一条一个 step
    - grammar 一条一个 step
    输出结构：
        { "type": "vocab" | "grammar", "index": i, "total": N, "data": {...} }
    """

    steps: list[dict] = []
    total = len(lesson["vocab"]) + len(lesson["grammar"])
    index = 0

    for vocab in lesson["vocab"]:
        steps.append({
            "type": "vocab",
            "index": index,
            "total": total,
            "data": vocab,
        })
        index += 1

    for grammar in lesson["grammar"]:
        steps.append({
            "type": "grammar",
            "index": index,
            "total": total,
            "data": grammar,
        })
        index += 1

    logger.debug(f"lesson steps generated: {len(steps)}")
    return steps


def get_step(lesson_id: str, step_index: int) -> Dict[str, Any]:
    """外部统一入口，返回指定步骤内容。"""

    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise ValueError(f"未找到课程：{lesson_id}")

    steps = get_lesson_steps(lesson)
    if step_index < 0 or step_index >= len(steps):
        raise IndexError(f"步骤索引越界：{step_index}")

    return steps[step_index]
