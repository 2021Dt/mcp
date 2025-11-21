class AIClient:
    def __init__(self, mode="ollama", model="qwen2.5:7b"):
        self.mode = mode
        self.model = model

    async def chat(self, messages, tools=None):
        if self.mode == "ollama":
            return await self._chat_ollama(messages, tools)
        elif self.mode == "api":
            return await self._chat_api(messages, tools)
        else:
            raise ValueError("未知 AI 模式")

    async def _chat_ollama(self, messages, tools):
        import ollama
        return ollama.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            think=False,
        )

    async def _chat_api(self, messages, tools):
        # TODO: 未来支持 GPT / DeepSeek / Doubao
        raise NotImplementedError("api 模式暂未实现")
