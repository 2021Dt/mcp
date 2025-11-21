from typing import List

from core.models import GrammarPoint
from core.utils.dp_log import LogFactory
from core.engines.grammar_rules import GRAMMAR_PATTERNS

logger = LogFactory.get_logger(__name__)


def detect_grammar(jp_text: str) -> List[GrammarPoint]:
    """简单遍历规则表并返回命中的语法点列表。"""

    results: List[GrammarPoint] = []
    lowered = jp_text.lower()

    for rule in GRAMMAR_PATTERNS:
        keywords = rule.get("pattern", [])
        if any(keyword in lowered for keyword in keywords):
            results.append(
                GrammarPoint(
                    name=rule.get("name", ""),
                    description=rule.get("description", ""),
                    example=rule.get("example", ""),
                )
            )
    logger.debug(f"detect_grammar matched {len(results)} items")
    return results
