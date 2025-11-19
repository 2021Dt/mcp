"""FastMCP 服务器入口文件。"""

from mcp_app import mcp

# 导入工具模块（不要删除）
import tools.japanese_chat_tools  # noqa: F401
import tools.lesson_tools  # noqa: F401
import tools.scenario_tools  # noqa: F401


if __name__ == "__main__":
    mcp.run()
