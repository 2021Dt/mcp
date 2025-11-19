"""FastMCP 实例初始化模块。"""

from mcp.server.fastmcp import FastMCP

# 创建全局唯一的 FastMCP 应用实例，供服务器与工具模块共享。
mcp = FastMCP("AI_Language_Trainer")

__all__ = ["mcp"]
