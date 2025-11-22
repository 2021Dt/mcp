"""
提示词管理类（PromptManager）

用于统一管理项目中的提示词模板，支持：
- 持久化存储（core/prompts 下的 .md 文件）
- 内存模板注册
- 动态加载与变量替换
- 基于当前文件位置自动解析项目根目录，保证在任何运行路径下都能正常找到模板目录

提供统一入口：register(), save(), load(), build()
用于构建最终可用于 LLM 的提示词内容。
"""

from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict


class PromptManager:
    """
    强一致性路径管理：
    以当前文件 __file__ 为基准，无论在哪运行都能找到 core/prompts/
    """

    # 获取项目根目录（再也不依赖工作目录）
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    # prompts 目录
    ROOT = PROJECT_ROOT / "core" / "prompts"

    _memory_templates: Dict[str, str] = {}

    @classmethod
    def register(cls, name: str, content: str):
        cls._memory_templates[name] = content

    @classmethod
    @lru_cache()
    def _load_file(cls, path: Path) -> Optional[str]:
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    @classmethod
    def load(cls, name: str) -> Optional[str]:
        # 内存优先
        if name in cls._memory_templates:
            return cls._memory_templates[name]

        file_path = cls.ROOT / f"{name}.md"
        return cls._load_file(file_path)

    @classmethod
    def build(cls, name: str, **vars) -> Optional[str]:
        template = cls.load(name)
        if template is None:
            return None

        for k, v in vars.items():
            template = template.replace(f"{{{k}}}", str(v))

        return template

    @classmethod
    def save(cls, name: str, content: str):
        cls.ROOT.mkdir(parents=True, exist_ok=True)
        file_path = cls.ROOT / f"{name}.md"
        file_path.write_text(content, encoding="utf-8")
        cls._load_file.cache_clear()

prompt_manager = PromptManager()

__all__ = ["prompt_manager"]

# if "__main__" == __name__:
#     prompt_manager = PromptManager()
#     print(prompt_manager.load('japanese_teacher'))