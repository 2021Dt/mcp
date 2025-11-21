from typing import Any, List, Dict


def convert_mcp_tools_to_ollama(tools: List[Any]) -> List[Dict[str, Any]]:
    """将 MCP 工具列表转换为 Ollama 兼容的工具定义。"""

    converted: List[Dict[str, Any]] = []
    for tool in tools:
        name = getattr(tool, "name", "") or ""
        description = getattr(tool, "description", "") or ""
        input_schema = getattr(tool, "input_schema", {}) or {}
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": input_schema,
                },
            }
        )
    return converted
