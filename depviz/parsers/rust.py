"""
Rust语言依赖解析器 / Rust language dependency parser

解析Rust文件中的 use 和 mod 语句。
Parses use and mod statements in Rust files.
"""

import re
from typing import Optional

from depviz.parsers.base import BaseParser


class RustParser(BaseParser):
    """
    Rust依赖解析器 / Rust dependency parser

    支持解析以下语法 / Supports parsing the following syntax:
    - use module::path;
    - use module::path::{item1, item2};
    - use module::path as alias;
    - use self::module;
    - use super::module;
    - use crate::module;
    - mod module;
    - mod module { ... }
    """

    # 匹配 use 语句 / Match use statements
    _USE_RE = re.compile(r"""^use\s+([\w:]+(?:\s*::\s*\{[^}]*\})?(?:\s+as\s+\w+)?)\s*;""", re.MULTILINE)
    # 匹配 mod 声明 / Match mod declarations
    _MOD_RE = re.compile(r"""^mod\s+(\w+)\s*(?:;|\{)""", re.MULTILINE)

    @property
    def language(self) -> str:
        """返回语言名称 / Return language name"""
        return "rust"

    @property
    def file_extensions(self) -> list[str]:
        """返回支持的文件扩展名 / Return supported file extensions"""
        return [".rs"]

    def parse(self, file_path: str, content: str) -> list[str]:
        """
        解析Rust文件，提取所有依赖模块 / Parse Rust file and extract all dependency modules

        Args:
            file_path: 文件路径 / File path
            content: 文件内容 / File content

        Returns:
            依赖模块路径列表 / List of dependency module paths
        """
        dependencies: list[str] = []

        # 移除注释 / Remove comments
        cleaned = self._remove_comments(content)

        # 解析 use 语句 / Parse use statements
        for match in self._USE_RE.finditer(cleaned):
            use_path = match.group(1).strip()
            # 移除 as alias 部分 / Remove 'as alias' part
            use_path = re.sub(r"\s+as\s+\w+\s*$", "", use_path)
            # 移除花括号部分 / Remove brace part
            use_path = re.sub(r"\s*::\s*\{[^}]*\}\s*$", "", use_path)
            # 忽略 self/super/crate 开头的内部引用
            # Ignore self/super/crate prefixed internal references
            if use_path.startswith("self::") or use_path.startswith("super::") or use_path.startswith("crate::"):
                # 取 crate:: 后面的部分 / Take the part after crate::
                if use_path.startswith("crate::"):
                    use_path = use_path[7:]
                else:
                    continue
            dep = self._clean_dependency(use_path)
            if dep:
                # 取顶层模块名（:: 分隔的第一个部分）/ Take top-level module name
                top_module = dep.split("::")[0]
                if top_module:
                    dependencies.append(top_module)

        # 解析 mod 声明 / Parse mod declarations
        for match in self._MOD_RE.finditer(cleaned):
            mod_name = match.group(1).strip()
            dep = self._clean_dependency(mod_name)
            if dep:
                dependencies.append(dep)

        # 去重 / Deduplicate
        return list(dict.fromkeys(dependencies))

    def _remove_comments(self, content: str) -> str:
        """
        移除Rust注释 / Remove Rust comments

        处理单行注释(//)和块注释(/* */)，包括嵌套块注释。
        Handles single-line (//) and block (/* */) comments, including nested ones.

        Args:
            content: 源代码 / Source code

        Returns:
            去除注释后的内容 / Content with comments removed
        """
        # 移除块注释（简化处理，不处理嵌套）/ Remove block comments (simplified, no nesting)
        content = re.sub(r"/\*[\s\S]*?\*/", "", content)
        # 移除单行注释 / Remove single-line comments
        content = re.sub(r"//[^\n]*", "", content)
        return content
