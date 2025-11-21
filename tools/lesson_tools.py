"""课程工具层：调用 lesson_engine 暴露给 MCP。"""

from mcp_app import mcp
from core.engines.lesson_engine import get_lesson, get_step


@mcp.tool()
def get_lesson_overview(lesson_id: str) -> dict:
    """返回课程概览，包括标题、等级、词汇与语法数量。"""

    lesson = get_lesson(lesson_id)
    if lesson is None:
        return {}
    return {
        "id": lesson.get("id"),
        "title": lesson.get("title"),
        "level": lesson.get("level"),
        "vocab_count": len(lesson.get("vocab", [])),
        "grammar_count": len(lesson.get("grammar", [])),
    }


@mcp.tool()
def get_lesson_step(lesson_id: str, step_index: int) -> dict:
    """按步骤返回课程具体内容。"""

    return get_step(lesson_id, step_index)
