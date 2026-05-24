"""
Python语言依赖解析器 / Python language dependency parser

解析Python文件中的 import 和 from...import 语句。
Parses import and from...import statements in Python files.
"""

import re
from typing import Optional

from depviz.parsers.base import BaseParser


class PythonParser(BaseParser):
    """
    Python依赖解析器 / Python dependency parser

    支持解析以下语法 / Supports parsing the following syntax:
    - import module
    - import module as alias
    - import module1, module2
    - from module import name
    - from module import name as alias
    - from module import name1, name2
    - from .module import name (相对导入，会被忽略 / relative imports, ignored)
    """

    # 匹配 import 语句的正则表达式 / Regex for import statements
    _IMPORT_RE = re.compile(r"^import\s+([\w., ]+)", re.MULTILINE)
    # 匹配 from...import 语句的正则表达式 / Regex for from...import statements
    _FROM_IMPORT_RE = re.compile(r"^from\s+([\w.]+)\s+import\s+", re.MULTILINE)

    @property
    def language(self) -> str:
        """返回语言名称 / Return language name"""
        return "python"

    @property
    def file_extensions(self) -> list[str]:
        """返回支持的文件扩展名 / Return supported file extensions"""
        return [".py", ".pyw"]

    def parse(self, file_path: str, content: str) -> list[str]:
        """
        解析Python文件，提取所有导入的模块 / Parse Python file and extract all imported modules

        Args:
            file_path: 文件路径 / File path
            content: 文件内容 / File content

        Returns:
            依赖模块名称列表 / List of dependency module names
        """
        dependencies: list[str] = []

        # 移除注释和字符串（简化处理）/ Remove comments and strings (simplified)
        cleaned = self._remove_comments(content)
        cleaned = self._remove_strings(cleaned)

        # 解析 import 语句 / Parse import statements
        for match in self._IMPORT_RE.finditer(cleaned):
            modules_str = match.group(1)
            # 处理多模块导入: import a, b, c / Handle multi-module imports
            for module in modules_str.split(","):
                dep = self._clean_dependency(module)
                if dep:
                    # 移除 'as alias' 部分 / Remove 'as alias' part
                    dep = re.sub(r"\s+as\s+\w+\s*$", "", dep)
                    # 取顶层模块名 / Take top-level module name
                    top_module = dep.split(".")[0]
                    if top_module:
                        dependencies.append(top_module)

        # 解析 from...import 语句 / Parse from...import statements
        for match in self._FROM_IMPORT_RE.finditer(cleaned):
            module = match.group(1).strip()
            # 忽略相对导入 / Ignore relative imports
            if module.startswith("."):
                continue
            dep = self._clean_dependency(module)
            if dep:
                dependencies.append(dep)

        # 去重 / Deduplicate
        return list(dict.fromkeys(dependencies))

    def _remove_strings(self, content: str) -> str:
        """
        移除Python字符串字面量（简化版）/ Remove Python string literals (simplified)

        防止字符串中的 import 关键字被误解析。
        Prevent import keywords inside strings from being falsely parsed.

        Args:
            content: 源代码 / Source code

        Returns:
            去除字符串后的内容 / Content with strings removed
        """
        # 移除三引号字符串 / Remove triple-quoted strings
        content = re.sub(r'"""[\s\S]*?"""', "", content)
        content = re.sub(r"'''[\s\S]*?'''", "", content)
        # 移除单/双引号字符串 / Remove single/double quoted strings
        content = re.sub(r'"[^"\n]*"', '""', content)
        content = re.sub(r"'[^'\n]*'", "''", content)
        return content
