"""硬编码的日语语法点规则库，供语法引擎进行快速匹配。"""

from typing import List, TypedDict


class GrammarPattern(TypedDict):
    """描述单个语法模式的关键要素。"""

    name: str
    pattern: List[str]
    description: str
    example: str


GRAMMAR_PATTERNS: List[GrammarPattern] = [
    {
        "name": "～うちに",
        "pattern": ["うちに"],
        "description": "在……期间；趁……的时候",
        "example": "雨が降らないうちに帰りましょう。",
    },
    {
        "name": "～てから",
        "pattern": ["てから"],
        "description": "做完前项之后再进行后项",
        "example": "宿題をしてから遊びに行きます。",
    },
    {
        "name": "～ば～ほど",
        "pattern": ["ば", "ほど"],
        "description": "越……越……的程度变化",
        "example": "勉強すればするほど上手になります。",
    },
    {
        "name": "～ばいい",
        "pattern": ["ばいい"],
        "description": "只要……就可以；应当……",
        "example": "分からなければ先生に聞けばいい。",
    },
    {
        "name": "～だけで",
        "pattern": ["だけで"],
        "description": "只凭……就；仅仅……就",
        "example": "君の声を聞くだけで元気になる。",
    },
    {
        "name": "～ところだ",
        "pattern": ["ところだ"],
        "description": "正要……；刚刚……；正在……的时候",
        "example": "今出かけるところだから、後で電話するね。",
    },
    {
        "name": "～ようにする",
        "pattern": ["ようにする"],
        "description": "尽量做到；努力保持某习惯",
        "example": "毎日日本語で日記を書くようにしています。",
    },
    {
        "name": "～ことにする",
        "pattern": ["ことにする"],
        "description": "决定做……；将……定为习惯",
        "example": "今年から早起きすることにしました。",
    },
    {
        "name": "～らしい",
        "pattern": ["らしい"],
        "description": "听说；好像有那种典型特征",
        "example": "彼は来ないらしいです。",
    },
    {
        "name": "～みたい",
        "pattern": ["みたい"],
        "description": "像……一样；似乎……",
        "example": "雨が降りそうみたいだ。",
    },
    {
        "name": "～つもり",
        "pattern": ["つもり"],
        "description": "打算……；原以为……",
        "example": "来週旅行に行くつもりです。",
    },
]
