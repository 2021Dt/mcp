"""课程工具占位模块。"""

from mcp_app import mcp


@mcp.tool()
def lesson_overview(lesson_id: str) -> dict:
    """占位课程工具，返回请求的课程标识。"""
    return {"lesson_id": lesson_id, "status": "占位"}
