"""
依赖图构建与分析模块 / Dependency graph construction and analysis module

提供有向依赖图的构建、循环依赖检测（DFS算法）、统计分析等功能。
Provides directed dependency graph construction, cycle detection (DFS algorithm),
and statistical analysis capabilities.
"""

import json
import os
from collections import defaultdict
from typing import Any, Optional, Set

from depviz.parsers import get_parser
from depviz.utils import detect_language, normalize_path, scan_files


class DependencyGraph:
    """
    依赖关系有向图 / Directed dependency graph

    使用邻接表表示文件之间的依赖关系。
    Uses adjacency list to represent dependencies between files.
    """

    def __init__(self, base_path: str) -> None:
        """
        初始化依赖图 / Initialize dependency graph

        Args:
            base_path: 项目根路径 / Project root path
        """
        self.base_path: str = os.path.abspath(base_path)
        # 邻接表：文件 -> 依赖的文件列表 / Adjacency list: file -> list of dependent files
        self._adjacency: dict[str, list[str]] = defaultdict(list)
        # 反向邻接表：文件 -> 被哪些文件依赖 / Reverse adjacency: file -> list of files that depend on it
        self._reverse_adjacency: dict[str, list[str]] = defaultdict(list)
        # 文件到语言的映射 / File to language mapping
        self._file_languages: dict[str, str] = {}
        # 文件到外部依赖的映射 / File to external dependencies mapping
        self._external_deps: dict[str, list[str]] = defaultdict(list)

    @property
    def files(self) -> list[str]:
        """获取所有已扫描的文件列表 / Get all scanned files"""
        return sorted(self._adjacency.keys())

    @property
    def file_count(self) -> int:
        """获取文件总数 / Get total file count"""
        return len(self._adjacency)

    @property
    def dependency_count(self) -> int:
        """获取依赖关系总数 / Get total dependency count"""
        return sum(len(deps) for deps in self._adjacency.values())

    @property
    def external_dependency_count(self) -> int:
        """获取外部依赖总数 / Get total external dependency count"""
        return sum(len(deps) for deps in self._external_deps.values())

    def add_dependency(self, from_file: str, to_file: str) -> None:
        """
        添加一条依赖关系 / Add a dependency edge

        Args:
            from_file: 源文件 / Source file
            to_file: 目标文件 / Target file
        """
        # 确保两个文件都在邻接表中注册 / Ensure both files are registered
        if from_file not in self._adjacency:
            self._adjacency[from_file] = []
        if to_file not in self._adjacency:
            self._adjacency[to_file] = []

        if to_file not in self._adjacency[from_file]:
            self._adjacency[from_file].append(to_file)
            self._reverse_adjacency[to_file].append(from_file)

    def add_external_dependency(self, from_file: str, dep_name: str) -> None:
        """
        添加外部依赖 / Add external dependency

        Args:
            from_file: 源文件 / Source file
            dep_name: 外部依赖名称 / External dependency name
        """
        if dep_name not in self._external_deps[from_file]:
            self._external_deps[from_file].append(dep_name)

    def get_dependencies(self, file_path: str) -> list[str]:
        """
        获取文件的所有内部依赖 / Get all internal dependencies of a file

        Args:
            file_path: 文件路径 / File path

        Returns:
            依赖文件列表 / List of dependent files
        """
        return self._adjacency.get(file_path, [])

    def get_dependents(self, file_path: str) -> list[str]:
        """
        获取依赖指定文件的所有文件 / Get all files that depend on the given file

        Args:
            file_path: 文件路径 / File path

        Returns:
            依赖方文件列表 / List of dependent files
        """
        return self._reverse_adjacency.get(file_path, [])

    def get_external_dependencies(self, file_path: str) -> list[str]:
        """
        获取文件的外部依赖 / Get external dependencies of a file

        Args:
            file_path: 文件路径 / File path

        Returns:
            外部依赖列表 / List of external dependencies
        """
        return self._external_deps.get(file_path, [])

    def detect_cycles(self) -> list[list[str]]:
        """
        使用DFS算法检测循环依赖 / Detect circular dependencies using DFS algorithm

        Returns:
            循环依赖路径列表，每条路径是一个文件名列表
            List of circular dependency paths, each path is a list of file names
        """
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            """深度优先搜索 / Depth-first search"""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self._adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # 找到循环 / Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for file_path in self.files:
            if file_path not in visited:
                dfs(file_path)

        return cycles

    def get_statistics(self) -> dict[str, Any]:
        """
        获取依赖统计信息 / Get dependency statistics

        Returns:
            统计信息字典 / Statistics dictionary
        """
        cycles = self.detect_cycles()

        # 计算语言分布 / Calculate language distribution
        lang_dist: dict[str, int] = defaultdict(int)
        for lang in self._file_languages.values():
            lang_dist[lang] += 1

        # 计算最大深度 / Calculate maximum depth
        max_depth = self._calculate_max_depth()

        return {
            "file_count": self.file_count,
            "dependency_count": self.dependency_count,
            "external_dependency_count": self.external_dependency_count,
            "cycle_count": len(cycles),
            "language_distribution": dict(lang_dist),
            "max_dependency_depth": max_depth,
            "most_depended_file": self._get_most_depended_file(),
        }

    def _calculate_max_depth(self) -> int:
        """
        计算依赖图的最大深度 / Calculate maximum depth of dependency graph

        Returns:
            最大深度 / Maximum depth
        """
        max_depth = 0
        visited: set[str] = set()

        def dfs(node: str, depth: int) -> None:
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            visited.add(node)
            for neighbor in self._adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, depth + 1)

        for file_path in self.files:
            if file_path not in visited:
                dfs(file_path, 0)

        return max_depth

    def _get_most_depended_file(self) -> Optional[str]:
        """
        获取被依赖最多的文件 / Get the most depended-upon file

        Returns:
            文件路径或None / File path or None
        """
        if not self._reverse_adjacency:
            return None
        return max(
            self._reverse_adjacency.items(),
            key=lambda x: len(x[1]),
        )[0]

    def to_dict(self) -> dict[str, Any]:
        """
        将依赖图导出为字典格式 / Export dependency graph as dictionary

        Returns:
            字典格式的依赖图数据 / Dependency graph data in dictionary format
        """
        return {
            "base_path": self.base_path,
            "files": self.files,
            "dependencies": {
                f: deps for f, deps in sorted(self._adjacency.items())
            },
            "external_dependencies": {
                f: deps for f, deps in sorted(self._external_deps.items())
            },
            "cycles": self.detect_cycles(),
            "statistics": self.get_statistics(),
        }

    def to_json(self, indent: int = 2) -> str:
        """
        将依赖图导出为JSON字符串 / Export dependency graph as JSON string

        Args:
            indent: 缩进空格数 / Number of indentation spaces

        Returns:
            JSON格式字符串 / JSON formatted string
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def build_graph(
    root_path: str,
    exclude_dirs: Optional[set[str]] = None,
    verbose: bool = False,
) -> DependencyGraph:
    """
    扫描目录并构建依赖图 / Scan directory and build dependency graph

    Args:
        root_path: 项目根路径 / Project root path
        exclude_dirs: 自定义排除目录 / Custom excluded directories
        verbose: 是否显示详细输出 / Whether to show verbose output

    Returns:
        构建好的依赖图 / Built dependency graph
    """
    root_path = os.path.abspath(root_path)
    graph = DependencyGraph(root_path)

    if verbose:
        print(f"[INFO] 开始扫描目录: {root_path}")
        print(f"[INFO] Start scanning directory: {root_path}")

    # 扫描所有源文件 / Scan all source files
    files = scan_files(root_path, exclude_dirs, verbose)

    if verbose:
        print(f"[INFO] 发现 {len(files)} 个源文件 / Found {len(files)} source files")

    # 构建文件名到相对路径的映射 / Build filename to relative path mapping
    file_map: dict[str, str] = {}
    for f in files:
        rel_path = normalize_path(f, root_path)
        file_map[rel_path] = f
        # 也用文件名（不含路径）建立映射 / Also map by filename (without path)
        basename = os.path.basename(f)
        name_without_ext = os.path.splitext(basename)[0]
        file_map[basename] = f
        file_map[name_without_ext] = f

    # 解析每个文件的依赖 / Parse dependencies for each file
    for file_path in files:
        rel_path = normalize_path(file_path, root_path)
        language = detect_language(file_path)

        if language is None:
            continue

        graph._file_languages[rel_path] = language

        # 确保文件在邻接表中注册（即使没有依赖）/ Ensure file is registered in adjacency list
        if rel_path not in graph._adjacency:
            graph._adjacency[rel_path] = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except (IOError, OSError) as e:
            if verbose:
                print(f"[WARN] 无法读取文件 {file_path}: {e}")
            continue

        try:
            parser = get_parser(language)
            dependencies = parser.parse(file_path, content)
        except ValueError as e:
            if verbose:
                print(f"[WARN] 解析器错误 {file_path}: {e}")
            continue

        for dep in dependencies:
            # 尝试将依赖名称映射到项目内的文件
            # Try to map dependency name to a file within the project
            resolved = _resolve_dependency(dep, file_map, root_path, language)
            if resolved:
                resolved_rel = normalize_path(resolved, root_path)
                graph.add_dependency(rel_path, resolved_rel)
            else:
                # 外部依赖 / External dependency
                graph.add_external_dependency(rel_path, dep)

    if verbose:
        print(f"[INFO] 依赖图构建完成 / Dependency graph built")
        print(f"[INFO] 文件数: {graph.file_count}, "
              f"依赖数: {graph.dependency_count}, "
              f"外部依赖数: {graph.external_dependency_count}")

    return graph


def _resolve_dependency(
    dep_name: str,
    file_map: dict[str, str],
    base_path: str,
    language: str,
) -> Optional[str]:
    """
    尝试将依赖名称解析为项目内的文件路径
    Try to resolve a dependency name to a file path within the project

    Args:
        dep_name: 依赖名称 / Dependency name
        file_map: 文件映射 / File mapping
        base_path: 基础路径 / Base path
        language: 编程语言 / Programming language

    Returns:
        解析到的文件绝对路径或None / Resolved absolute file path or None
    """
    # 直接匹配文件名 / Direct filename match
    if dep_name in file_map:
        return file_map[dep_name]

    # 尝试添加常见扩展名 / Try adding common extensions
    ext_map: dict[str, list[str]] = {
        "python": [".py"],
        "javascript": [".js", ".ts", ".jsx", ".tsx"],
        "golang": [".go"],
        "rust": [".rs"],
        "java": [".java"],
    }
    extensions = ext_map.get(language, [])
    for ext in extensions:
        candidate = dep_name + ext
        if candidate in file_map:
            return file_map[candidate]

    # 对于Python，尝试将点号替换为路径分隔符
    # For Python, try replacing dots with path separators
    if language == "python":
        path_candidate = dep_name.replace(".", "/") + ".py"
        if path_candidate in file_map:
            return file_map[path_candidate]
        # 尝试作为包目录下的 __init__.py / Try as __init__.py in a package directory
        init_candidate = dep_name.replace(".", "/") + "/__init__.py"
        if init_candidate in file_map:
            return file_map[init_candidate]

    # 对于Java，尝试将点号替换为路径分隔符
    # For Java, try replacing dots with path separators
    if language == "java":
        path_candidate = dep_name.replace(".", "/") + ".java"
        if path_candidate in file_map:
            return file_map[path_candidate]

    return None
