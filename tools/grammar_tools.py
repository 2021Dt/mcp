"""提供日语语法识别相关的 MCP 工具。"""

from mcp_app import mcp
from core.engines.grammar_engine import detect_grammar


@mcp.tool()
def jp_detect_grammar(text: str) -> list[dict]:
    """外部工具：识别文本中的日语语法点。"""

    return detect_grammar(text)
