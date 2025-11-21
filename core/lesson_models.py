"""课程（Lesson）相关的数据结构与样例数据。"""

from typing import List, TypedDict


class VocabItem(TypedDict):
    """词汇项，包含日语、读音、中文释义与示例。"""

    jp: str
    reading: str
    zh: str
    example: str


class GrammarItem(TypedDict):
    """语法项，包含名称、结构、解释、示例与等级。"""

    name: str
    pattern: str
    explanation: str
    examples: List[str]
    level: str  # N5~N1


class Lesson(TypedDict):
    """课程定义，聚合词汇与语法。"""

    id: str
    title: str
    level: str
    vocab: List[VocabItem]
    grammar: List[GrammarItem]


SAMPLE_LESSONS: List[Lesson] = [
    {
        "id": "n5_lesson_01",
        "title": "自我介绍入门",
        "level": "N5",
        "vocab": [
            {
                "jp": "はじめまして",
                "reading": "はじめまして",
                "zh": "初次见面",
                "example": "はじめまして、山田です。",
            },
            {
                "jp": "よろしくお願いします",
                "reading": "よろしくおねがいします",
                "zh": "请多关照",
                "example": "これからよろしくお願いします。",
            },
            {
                "jp": "学生",
                "reading": "がくせい",
                "zh": "学生",
                "example": "私は学生です。",
            },
            {
                "jp": "会社員",
                "reading": "かいしゃいん",
                "zh": "公司职员",
                "example": "父は会社員です。",
            },
        ],
        "grammar": [
            {
                "name": "～です",
                "pattern": "名词 + です",
                "explanation": "表示判断或说明，礼貌体。",
                "examples": ["私は学生です。", "田中さんは会社員です。"],
                "level": "N5",
            },
            {
                "name": "～は～です",
                "pattern": "名词1 は 名词2 です",
                "explanation": "提示主题并进行说明。",
                "examples": ["私は山田です。", "これは本です。"],
                "level": "N5",
            },
            {
                "name": "～も",
                "pattern": "名词 も",
                "explanation": "表示“也”，与前项并列。",
                "examples": ["私も学生です。", "彼も日本人です。"],
                "level": "N5",
            },
        ],
    }
]
