from core.utils.dp_log import LogFactory

logger = LogFactory.get_logger(__name__)

GRAMMAR_PATTERNS = [
    {
        "name": "～うちに",
        "pattern": ["うちに"],
        "description": "趁着某状态持续期间做某事。",
        "example": "学生のうちにもっと勉強すべきだ。",
    },
    {
        "name": "～てもいい",
        "pattern": ["てもいい"],
        "description": "表示许可或允许。",
        "example": "ここに座ってもいいですか。",
    },
    {
        "name": "～から",
        "pattern": ["から"],
        "description": "表示原因或理由。",
        "example": "雨が降っているから、傘を持って行きます。",
    },
]
