"""基于硬编码规则的简易语法识别引擎。"""

from __future__ import annotations

from typing import List, TYPE_CHECKING

from core.grammar_rules import GRAMMAR_PATTERNS, GrammarPattern

if TYPE_CHECKING:  # 避免运行时循环依赖
    from core.conversation_engine import GrammarPoint
else:
    GrammarPoint = dict


def detect_grammar(jp_text: str) -> List[GrammarPoint]:
    """输入日语文本，输出识别到的所有语法点列表（简单包含匹配版）。"""

    results: List[GrammarPoint] = []
    for pattern in GRAMMAR_PATTERNS:
        for key in pattern["pattern"]:
            if key and key in jp_text:
                results.append(
                    {
                        "name": pattern["name"],
                        "description": pattern["description"],
                        "example": pattern["example"],
                    }
                )
                break
    return results
