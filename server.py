"""FastMCP 服务器入口文件，兼容异步工具。"""

from mcp_app import mcp

# 导入工具模块（不要删除）
import tools.japanese_chat_tools  # noqa: F401
import tools.lesson_tools  # noqa: F401
import tools.scenario_tools  # noqa: F401


def main() -> None:
    """启动 MCP 服务器，FastMCP 内部会调度异步工具。"""

    mcp.run()


if __name__ == "__main__":
    main()
