"""课程分步教学引擎。"""

from typing import Any, Dict, Optional

from core.lesson_models import SAMPLE_LESSONS
from core.models import GrammarItem, Lesson, VocabItem


def get_lesson(lesson_id: str) -> Optional[Lesson]:
    """根据 lesson_id 查找 Lesson。"""

    for lesson in SAMPLE_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
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
