"""课程相关的 MCP 工具。"""

from mcp_app import mcp
from core.lesson_engine import get_lesson, get_step


@mcp.tool()
def get_lesson_overview(lesson_id: str) -> dict:
    """
    返回 lesson 的基本信息，包括：
    - title
    - level
    - vocab_count
    - grammar_count
    """

    lesson = get_lesson(lesson_id)
    if lesson is None:
        raise ValueError(f"未找到课程：{lesson_id}")

    return {
        "id": lesson["id"],
        "title": lesson["title"],
        "level": lesson["level"],
        "vocab_count": len(lesson["vocab"]),
        "grammar_count": len(lesson["grammar"]),
    }


@mcp.tool()
def get_lesson_step(lesson_id: str, step_index: int) -> dict:
    """返回课程第 step_index 步的内容。"""

    return get_step(lesson_id, step_index)
