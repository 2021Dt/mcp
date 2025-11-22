"""AI 模块，简单封装了一下 ollama"""

import ollama

def _format_size(bytes_val: int) -> str:
    """将字节转换为可读单位"""
    if bytes_val >= 1024 ** 3:
        return f"{bytes_val / (1024 ** 3):.2f} GB"
    elif bytes_val >= 1024 ** 2:
        return f"{bytes_val / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes_val / 1024:.2f} KB"


class AIClient:
    def __init__(self, mode="ollama", model=None):
        self.mode = mode
        models_info = self.check_model()
        models = models_info.get("models", [])

        # 如果没有模型，自动Fallback到传入的默认模型名称
        if not models:
            print("本地 Ollama 无可用模型")
            # self.model = {"name": model, "size": "0", "size_bytes": 0}
        elif not model:
            # 正常情况：取第一个模型
            self.model = models[0].get("name")
        else:
            self.model = model

    def check_model(self) -> dict:
        try:
            resp = ollama.list()
        except Exception as e:
            return {
                "count": 0,
                "models": [],
                "error": str(e)
            }

        result = []

        for m in resp.models:
            result.append({
                "name": m.model,
                "size": _format_size(m.size),
                "size_bytes": m.size,
                "modified_at": str(m.modified_at),
                "quantization": m.details.quantization_level,
            })

        # 从小到大排序
        result.sort(key=lambda x: x["size_bytes"])

        return {
            "count": len(result),
            "models": result
        }


    async def chat(self, messages, tools=None):
        if self.mode == "ollama":
            return await self._chat_ollama(messages, tools)
        elif self.mode == "api":
            return await self._chat_api(messages, tools)
        else:
            raise ValueError("未知 AI 模式")

    async def _chat_ollama(self, messages, tools):
        return ollama.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            think=False,
        )

    async def _chat_api(self, messages, tools):
        # TODO: 未来支持 GPT / DeepSeek / Doubao
        raise NotImplementedError("api 模式暂未实现")
