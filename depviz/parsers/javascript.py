"""
JavaScript/TypeScript语言依赖解析器 / JavaScript/TypeScript dependency parser

解析JS/TS文件中的 require()、import、export 语句。
Parses require(), import, and export statements in JS/TS files.
"""

import re
from typing import Optional

from depviz.parsers.base import BaseParser


class JavaScriptParser(BaseParser):
    """
    JavaScript/TypeScript依赖解析器 / JavaScript/TypeScript dependency parser

    支持解析以下语法 / Supports parsing the following syntax:
    - require('module')
    - require("module")
    - import 'module'
    - import Module from 'module'
    - import { name } from 'module'
    - import * as name from 'module'
    - export ... from 'module'
    - dynamic import: import('module')
    """

    # 匹配 require() 调用 / Match require() calls
    _REQUIRE_RE = re.compile(r"""(?:^|[=({\s,;])require\s*\(\s*["']([^"']+)["']\s*\)""")
    # 匹配静态 import 语句 / Match static import statements
    _IMPORT_RE = re.compile(
        r"""^import\s+(?:(?:[\w*\s{},]*\s+from\s+)?["']([^"']+)["']|["']([^"']+)["'])""",
        re.MULTILINE,
    )
    # 匹配 export ... from 语句 / Match export ... from statements
    _EXPORT_FROM_RE = re.compile(
        r"""^export\s+(?:(?:[\w*\s{},]+\s+)?from\s+)?["']([^"']+)["']""",
        re.MULTILINE,
    )
    # 匹配动态 import() 调用 / Match dynamic import() calls
    _DYNAMIC_IMPORT_RE = re.compile(r"""import\s*\(\s*["']([^"']+)["']\s*\)""")

    @property
    def language(self) -> str:
        """返回语言名称 / Return language name"""
        return "javascript"

    @property
    def file_extensions(self) -> list[str]:
        """返回支持的文件扩展名 / Return supported file extensions"""
        return [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"]

    def parse(self, file_path: str, content: str) -> list[str]:
        """
        解析JS/TS文件，提取所有依赖模块 / Parse JS/TS file and extract all dependency modules

        Args:
            file_path: 文件路径 / File path
            content: 文件内容 / File content

        Returns:
            依赖模块路径列表 / List of dependency module paths
        """
        dependencies: list[str] = []

        # 移除注释 / Remove comments
        cleaned = self._remove_js_comments(content)

        # 先在原始内容上提取依赖，再过滤字符串内的误匹配
        # Extract dependencies from original content, then filter false matches from strings
        string_ranges = self._find_string_ranges(cleaned)

        # 解析 require() / Parse require()
        for match in self._REQUIRE_RE.finditer(cleaned):
            if not self._is_in_string(match.start(), string_ranges):
                dep = self._clean_dependency(match.group(1))
                if dep:
                    dependencies.append(dep)

        # 解析静态 import / Parse static import
        for match in self._IMPORT_RE.finditer(cleaned):
            if not self._is_in_string(match.start(), string_ranges):
                # group(1) 是 from 'module' 中的 module，group(2) 是 import 'module' 中的 module
                dep_str = match.group(1) or match.group(2)
                if dep_str:
                    dep = self._clean_dependency(dep_str)
                    if dep:
                        dependencies.append(dep)

        # 解析 export ... from / Parse export ... from
        for match in self._EXPORT_FROM_RE.finditer(cleaned):
            if not self._is_in_string(match.start(), string_ranges):
                dep = self._clean_dependency(match.group(1))
                if dep:
                    dependencies.append(dep)

        # 解析动态 import() / Parse dynamic import()
        for match in self._DYNAMIC_IMPORT_RE.finditer(cleaned):
            if not self._is_in_string(match.start(), string_ranges):
                dep = self._clean_dependency(match.group(1))
                if dep:
                    dependencies.append(dep)

        # 去重 / Deduplicate
        return list(dict.fromkeys(dependencies))

    def _remove_js_comments(self, content: str) -> str:
        """
        移除JS/TS注释 / Remove JS/TS comments

        处理单行注释(//)和多行注释(/* */)。
        Handles single-line (//) and multi-line (/* */) comments.

        Args:
            content: 源代码 / Source code

        Returns:
            去除注释后的内容 / Content with comments removed
        """
        # 先处理多行注释 / Handle multi-line comments first
        content = re.sub(r"/\*[\s\S]*?\*/", "", content)
        # 再处理单行注释 / Then handle single-line comments
        content = re.sub(r"//[^\n]*", "", content)
        return content

    def _find_string_ranges(self, content: str) -> list[tuple[int, int]]:
        """
        查找内容中所有字符串字面量的位置范围
        Find position ranges of all string literals in content

        Args:
            content: 源代码（已移除注释）/ Source code (comments removed)

        Returns:
            (start, end) 位置元组列表 / List of (start, end) position tuples
        """
        ranges: list[tuple[int, int]] = []
        i = 0
        n = len(content)
        while i < n:
            ch = content[i]
            if ch in ('"', "'", '`'):
                quote = ch
                start = i
                i += 1
                while i < n:
                    if content[i] == '\\':
                        i += 2  # 跳过转义字符 / Skip escaped character
                        continue
                    if content[i] == quote:
                        i += 1
                        break
                    i += 1
                ranges.append((start, i))
            else:
                i += 1
        return ranges

    def _is_in_string(self, pos: int, string_ranges: list[tuple[int, int]]) -> bool:
        """
        检查给定位置是否在某个字符串内部 / Check if position is inside a string

        Args:
            pos: 位置 / Position
            string_ranges: 字符串范围列表 / String range list

        Returns:
            是否在字符串内 / Whether inside a string
        """
        for start, end in string_ranges:
            if start <= pos < end:
                return True
        return False
