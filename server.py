"""FastMCP 服务器入口文件，兼容异步工具。"""

from core.utils.dp_log import LogFactory

LogFactory.configure_global(enable_console=True)

from mcp_app import mcp  # noqa: E402

# 导入工具模块（不要删除）
import tools.japanese_chat_tools  # noqa: F401,E402
import tools.lesson_tools  # noqa: F401,E402
import tools.scenario_tools  # noqa: F401,E402
import tools.ollama_tools  # noqa: F401,E402
import tools.grammar_tools  # noqa: F401,E402
import tools.user_state_tools  # noqa: F401,E402


def main() -> None:
    """启动 MCP 服务器，FastMCP 内部会调度异步工具。"""

    mcp.run()


if __name__ == "__main__":
    main()
