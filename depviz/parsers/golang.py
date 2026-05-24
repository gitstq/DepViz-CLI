"""
Go语言依赖解析器 / Go language dependency parser

解析Go文件中的 import 语句。
Parses import statements in Go files.
"""

import re
from typing import Optional

from depviz.parsers.base import BaseParser


class GolangParser(BaseParser):
    """
    Go依赖解析器 / Go dependency parser

    支持解析以下语法 / Supports parsing the following syntax:
    - import "module"
    - import 'module'
    - import `module`
    - import ( "module1" "module2" ... )
    - import alias "module"
    - import _ "module" (blank import)
    - import . "module" (dot import)
    """

    # 匹配单行 import / Match single-line import
    _IMPORT_SINGLE_RE = re.compile(
        r"""^import\s+(?:[\w_.]+\s+)?["'`]([^"'`]+)["'`]""",
        re.MULTILINE,
    )
    # 匹配多行 import 块 / Match multi-line import block
    _IMPORT_BLOCK_RE = re.compile(r"""import\s*\(([^)]+)\)""", re.DOTALL)
    # 在 import 块内匹配模块路径 / Match module paths within import block
    _IMPORT_PATH_RE = re.compile(r"""["'`]([^"'`]+)["'`]""")

    @property
    def language(self) -> str:
        """返回语言名称 / Return language name"""
        return "golang"

    @property
    def file_extensions(self) -> list[str]:
        """返回支持的文件扩展名 / Return supported file extensions"""
        return [".go"]

    def parse(self, file_path: str, content: str) -> list[str]:
        """
        解析Go文件，提取所有导入的包 / Parse Go file and extract all imported packages

        Args:
            file_path: 文件路径 / File path
            content: 文件内容 / File content

        Returns:
            依赖包路径列表 / List of dependency package paths
        """
        dependencies: list[str] = []

        # 移除注释 / Remove comments
        cleaned = self._remove_comments(content)

        # 解析单行 import / Parse single-line import
        for match in self._IMPORT_SINGLE_RE.finditer(cleaned):
            dep = self._clean_dependency(match.group(1))
            if dep:
                dependencies.append(dep)

        # 解析多行 import 块 / Parse multi-line import block
        for match in self._IMPORT_BLOCK_RE.finditer(cleaned):
            block_content = match.group(1)
            for path_match in self._IMPORT_PATH_RE.finditer(block_content):
                dep = self._clean_dependency(path_match.group(1))
                if dep:
                    dependencies.append(dep)

        # 去重 / Deduplicate
        return list(dict.fromkeys(dependencies))

    def _remove_comments(self, content: str) -> str:
        """
        移除Go注释 / Remove Go comments

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
