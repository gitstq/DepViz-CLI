"""
解析器包 / Parsers package

提供各编程语言的依赖关系解析器。
Provides dependency parsers for various programming languages.
"""

from depviz.parsers.base import BaseParser
from depviz.parsers.python import PythonParser
from depviz.parsers.javascript import JavaScriptParser
from depviz.parsers.golang import GolangParser
from depviz.parsers.rust import RustParser
from depviz.parsers.java import JavaParser

# 语言名称到解析器类的映射 / Language name to parser class mapping
PARSER_REGISTRY: dict[str, type[BaseParser]] = {
    "python": PythonParser,
    "javascript": JavaScriptParser,
    "golang": GolangParser,
    "rust": RustParser,
    "java": JavaParser,
}


def get_parser(language: str) -> BaseParser:
    """
    根据语言名称获取对应的解析器实例 / Get parser instance by language name

    Args:
        language: 语言名称 / Language name

    Returns:
        解析器实例 / Parser instance

    Raises:
        ValueError: 不支持的语言 / Unsupported language
    """
    parser_cls = PARSER_REGISTRY.get(language)
    if parser_cls is None:
        supported = ", ".join(sorted(PARSER_REGISTRY.keys()))
        raise ValueError(
            f"不支持的语言: {language}，支持的语言: {supported} / "
            f"Unsupported language: {language}, supported: {supported}"
        )
    return parser_cls()


__all__ = [
    "BaseParser",
    "PythonParser",
    "JavaScriptParser",
    "GolangParser",
    "RustParser",
    "JavaParser",
    "PARSER_REGISTRY",
    "get_parser",
]
