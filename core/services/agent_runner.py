class AgentRunner:
    def __init__(self, ai_client, mcp_client):
        self.ai = ai_client
        self.mcp = mcp_client

    async def run(self, prompt: str):
        from core.services.ai_client_utils import convert_mcp_tools_to_ollama

        messages = [
            {"role": "system", "content": "使用中文回复用户"},
            {"role": "user", "content": prompt},
        ]

        async with self.mcp:
            await self.mcp.ping()
            tools = await self.mcp.list_tools()
            ollama_tools = convert_mcp_tools_to_ollama(tools)

            for _ in range(8):
                result = await self.ai.chat(messages, tools=ollama_tools)
                msg = result["message"]

                if "tool_calls" not in msg:
                    return msg["content"]

                for call in msg["tool_calls"]:
                    tool = call["function"]["name"]
                    args = call["function"]["arguments"]
                    try:
                        output = await self.mcp.call_tool(tool, args)
                    except Exception as e:
                        output = {"error": str(e)}

                    messages.append({
                        "role": "tool",
                        "name": tool,
                        "content": str(output)
                    })

            return "⚠️ 工具调用超过限制"
