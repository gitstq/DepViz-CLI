"""
解析器基类 / Base parser class

所有语言解析器的抽象基类，定义统一的解析接口。
Abstract base class for all language parsers, defining a unified parsing interface.
"""

import re
from abc import ABC, abstractmethod
from typing import Optional


class BaseParser(ABC):
    """
    依赖解析器基类 / Base dependency parser class

    所有语言解析器必须继承此类并实现 parse 方法。
    All language parsers must inherit from this class and implement the parse method.
    """

    @property
    @abstractmethod
    def language(self) -> str:
        """
        解析器支持的语言名称 / Language name supported by this parser

        Returns:
            语言名称字符串 / Language name string
        """
        ...

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """
        解析器支持的文件扩展名列表 / List of file extensions supported by this parser

        Returns:
            扩展名列表 / List of extensions
        """
        ...

    @abstractmethod
    def parse(self, file_path: str, content: str) -> list[str]:
        """
        解析文件内容，提取依赖项 / Parse file content and extract dependencies

        Args:
            file_path: 文件路径（用于相对导入解析）/ File path (for resolving relative imports)
            content: 文件内容 / File content

        Returns:
            依赖项列表 / List of dependencies
        """
        ...

    def _clean_dependency(self, dep: str) -> Optional[str]:
        """
        清理依赖项字符串 / Clean dependency string

        移除引号、多余空格等 / Remove quotes, extra spaces, etc.

        Args:
            dep: 原始依赖字符串 / Raw dependency string

        Returns:
            清理后的字符串或None / Cleaned string or None
        """
        dep = dep.strip()
        # 移除引号 / Remove quotes
        dep = dep.strip("\"'")
        # 移除行尾注释 / Remove trailing comments
        if " #" in dep:
            dep = dep[: dep.index(" #")].strip()
        if " //" in dep:
            dep = dep[: dep.index(" //")].strip()
        # 过滤空字符串和内置模块 / Filter empty strings and built-in modules
        if not dep or dep.startswith("."):
            return None
        return dep

    def _remove_comments(self, content: str) -> str:
        """
        移除代码中的注释（简化版）/ Remove comments from code (simplified version)

        注意：这是一个简化实现，可能无法处理所有边界情况。
        Note: This is a simplified implementation that may not handle all edge cases.

        Args:
            content: 源代码内容 / Source code content

        Returns:
            去除注释后的内容 / Content with comments removed
        """
        # 移除单行注释 / Remove single-line comments
        content = re.sub(r"#[^\n]*", "", content)       # Python/Rust
        content = re.sub(r"//[^\n]*", "", content)      # JS/TS/Go/Rust/Java
        return content
