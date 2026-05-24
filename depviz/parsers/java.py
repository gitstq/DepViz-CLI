"""
Java语言依赖解析器 / Java language dependency parser

解析Java文件中的 import 和 package 语句。
Parses import and package statements in Java files.
"""

import re
from typing import Optional

from depviz.parsers.base import BaseParser


class JavaParser(BaseParser):
    """
    Java依赖解析器 / Java dependency parser

    支持解析以下语法 / Supports parsing the following syntax:
    - import package.Class;
    - import package.*;
    - import static package.Class.method;
    - package com.example;
    """

    # 匹配 import 语句 / Match import statements
    _IMPORT_RE = re.compile(
        r"""^import\s+(?:static\s+)?([\w.]+(?:\.\*)?)\s*;""",
        re.MULTILINE,
    )
    # 匹配 package 声明 / Match package declarations
    _PACKAGE_RE = re.compile(r"""^package\s+([\w.]+)\s*;""", re.MULTILINE)

    @property
    def language(self) -> str:
        """返回语言名称 / Return language name"""
        return "java"

    @property
    def file_extensions(self) -> list[str]:
        """返回支持的文件扩展名 / Return supported file extensions"""
        return [".java"]

    def parse(self, file_path: str, content: str) -> list[str]:
        """
        解析Java文件，提取所有导入的包和类 / Parse Java file and extract all imported packages and classes

        Args:
            file_path: 文件路径 / File path
            content: 文件内容 / File content

        Returns:
            依赖包/类路径列表 / List of dependency package/class paths
        """
        dependencies: list[str] = []

        # 移除注释 / Remove comments
        cleaned = self._remove_comments(content)

        # 解析 import 语句 / Parse import statements
        for match in self._IMPORT_RE.finditer(cleaned):
            dep = self._clean_dependency(match.group(1))
            if dep:
                dependencies.append(dep)

        # 解析 package 声明（作为元数据）/ Parse package declarations (as metadata)
        # package 声明不作为依赖，但可以用于解析相对路径
        # Package declarations are not dependencies but can be used for resolving relative paths

        # 去重 / Deduplicate
        return list(dict.fromkeys(dependencies))

    def _remove_comments(self, content: str) -> str:
        """
        移除Java注释 / Remove Java comments

        处理单行注释(//)和块注释(/* */)，以及Javadoc注释(/** */)。
        Handles single-line (//), block (/* */), and Javadoc (/** */) comments.

        Args:
            content: 源代码 / Source code

        Returns:
            去除注释后的内容 / Content with comments removed
        """
        # 移除块注释和Javadoc / Remove block and Javadoc comments
        content = re.sub(r"/\*[\s\S]*?\*/", "", content)
        # 移除单行注释 / Remove single-line comments
        content = re.sub(r"//[^\n]*", "", content)
        return content
