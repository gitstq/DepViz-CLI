"""
终端可视化模块 / Terminal visualization module

提供依赖关系的树形视图和ASCII环形图可视化。
Provides tree view and ASCII ring chart visualization for dependency relationships.
"""

import math
import os
from typing import Any, Optional

from depviz.graph import DependencyGraph


class TreeVisualizer:
    """
    树形视图可视化器 / Tree view visualizer

    以缩进树形结构展示文件依赖关系。
    Displays file dependency relationships as an indented tree structure.
    """

    # 树形连接字符 / Tree connection characters
    BRANCH = "├── "
    LAST_BRANCH = "└── "
    VERTICAL = "│   "
    SPACE = "    "

    def __init__(self, graph: DependencyGraph) -> None:
        """
        初始化树形可视化器 / Initialize tree visualizer

        Args:
            graph: 依赖图 / Dependency graph
        """
        self.graph = graph

    def render(self, max_depth: int = 5, show_external: bool = False) -> str:
        """
        渲染树形视图 / Render tree view

        Args:
            max_depth: 最大显示深度 / Maximum display depth
            show_external: 是否显示外部依赖 / Whether to show external dependencies

        Returns:
            树形视图字符串 / Tree view string
        """
        lines: list[str] = []
        lines.append(f"依赖树 / Dependency Tree ({self.graph.base_path})")
        lines.append("=" * 60)

        visited: set[str] = set()

        for file_path in self.graph.files:
            if file_path not in visited:
                self._render_tree(
                    file_path, lines, "", True, max_depth, show_external, visited
                )

        lines.append("=" * 60)
        lines.append(f"共 {len(visited)} 个文件 / {len(visited)} files total")

        return "\n".join(lines)

    def _render_tree(
        self,
        node: str,
        lines: list[str],
        prefix: str,
        is_last: bool,
        max_depth: int,
        show_external: bool,
        visited: set[str],
        depth: int = 0,
    ) -> None:
        """
        递归渲染树节点 / Recursively render tree nodes

        Args:
            node: 当前节点 / Current node
            lines: 输出行列表 / Output line list
            prefix: 前缀字符串 / Prefix string
            is_last: 是否是最后一个兄弟节点 / Whether it's the last sibling
            max_depth: 最大深度 / Maximum depth
            show_external: 是否显示外部依赖 / Whether to show external dependencies
            visited: 已访问节点集合 / Visited nodes set
            depth: 当前深度 / Current depth
        """
        if depth > max_depth or node in visited:
            if node in visited and depth <= max_depth:
                connector = self.LAST_BRANCH if is_last else self.BRANCH
                lines.append(f"{prefix}{connector}{node} (已访问/visited)")
            return

        visited.add(node)

        # 添加当前节点 / Add current node
        if depth == 0:
            lines.append(f"{node}")
        else:
            connector = self.LAST_BRANCH if is_last else self.BRANCH
            lines.append(f"{prefix}{connector}{node}")

        # 获取子节点 / Get child nodes
        children = self.graph.get_dependencies(node)
        ext_deps = self.graph.get_external_dependencies(node) if show_external else []

        if not children and not ext_deps:
            return

        # 计算新的前缀 / Calculate new prefix
        if depth == 0:
            new_prefix = ""
        else:
            new_prefix = prefix + (self.SPACE if is_last else self.VERTICAL)

        # 渲染内部依赖子节点 / Render internal dependency child nodes
        for i, child in enumerate(children):
            is_child_last = (i == len(children) - 1) and not ext_deps
            self._render_tree(
                child, lines, new_prefix, is_child_last,
                max_depth, show_external, visited, depth + 1,
            )

        # 渲染外部依赖 / Render external dependencies
        if show_external and ext_deps:
            for i, ext_dep in enumerate(ext_deps):
                is_ext_last = i == len(ext_deps) - 1
                connector = self.LAST_BRANCH if is_ext_last else self.BRANCH
                lines.append(f"{new_prefix}{connector}[ext] {ext_dep}")


class RingVisualizer:
    """
    ASCII环形图可视化器 / ASCII ring chart visualizer

    使用ASCII字符在终端中绘制环形依赖关系图。
    Uses ASCII characters to draw a ring-shaped dependency chart in the terminal.
    """

    def __init__(self, graph: DependencyGraph) -> None:
        """
        初始化环形图可视化器 / Initialize ring visualizer

        Args:
            graph: 依赖图 / Dependency graph
        """
        self.graph = graph

    def render(self, width: int = 80, height: int = 40) -> str:
        """
        渲染环形依赖图 / Render ring dependency chart

        Args:
            width: 画布宽度 / Canvas width
            height: 画布高度 / Canvas height

        Returns:
            环形图字符串 / Ring chart string
        """
        lines: list[str] = []
        lines.append(f"环形依赖图 / Ring Dependency Chart ({self.graph.base_path})")
        lines.append("=" * width)

        files = self.graph.files
        if not files:
            lines.append("  (无文件 / No files)")
            return "\n".join(lines)

        # 创建画布 / Create canvas
        canvas = self._create_canvas(width, height - 4)

        # 计算环形布局 / Calculate ring layout
        center_x = width // 2
        center_y = (height - 4) // 2
        radius = min(center_x, center_y) - 4

        if radius < 3:
            lines.append("  画布太小，无法绘制 / Canvas too small to render")
            return "\n".join(lines)

        # 放置文件节点在环形上 / Place file nodes on the ring
        positions: dict[str, tuple[int, int]] = {}
        n = len(files)
        for i, file_path in enumerate(files):
            angle = 2 * math.pi * i / n - math.pi / 2  # 从顶部开始 / Start from top
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            # 限制在画布范围内 / Clamp within canvas bounds
            x = max(1, min(width - 2, x))
            y = max(0, min(height - 6, y))
            positions[file_path] = (x, y)

            # 在画布上放置节点标记 / Place node marker on canvas
            label = self._shorten_path(file_path, 12)
            self._draw_node(canvas, x, y, label, width, height - 4)

        # 绘制依赖连线 / Draw dependency lines
        for file_path, deps in self.graph._adjacency.items():
            if file_path not in positions:
                continue
            x1, y1 = positions[file_path]
            for dep in deps:
                if dep in positions:
                    x2, y2 = positions[dep]
                    self._draw_line(canvas, x1, y1, x2, y2, width, height - 4)

        # 将画布转换为字符串 / Convert canvas to string
        for row in canvas:
            lines.append("".join(row))

        lines.append("=" * width)

        # 显示循环依赖 / Show circular dependencies
        cycles = self.graph.detect_cycles()
        if cycles:
            lines.append(f"\n检测到 {len(cycles)} 个循环依赖 / {len(cycles)} cycle(s) detected:")
            for i, cycle in enumerate(cycles[:5], 1):  # 最多显示5个 / Show at most 5
                cycle_str = " -> ".join(
                    self._shorten_path(f, 20) for f in cycle
                )
                lines.append(f"  {i}. {cycle_str}")
            if len(cycles) > 5:
                lines.append(f"  ... 还有 {len(cycles) - 5} 个 / ... and {len(cycles) - 5} more")

        return "\n".join(lines)

    def _create_canvas(self, width: int, height: int) -> list[list[str]]:
        """
        创建空白画布 / Create blank canvas

        Args:
            width: 宽度 / Width
            height: 高度 / Height

        Returns:
            二维字符数组 / 2D character array
        """
        return [[" " for _ in range(width)] for _ in range(height)]

    def _draw_node(self, canvas: list[list[str]], x: int, y: int, label: str, width: int, height: int) -> None:
        """
        在画布上绘制节点 / Draw node on canvas

        Args:
            canvas: 画布 / Canvas
            x: X坐标 / X coordinate
            y: Y坐标 / Y coordinate
            label: 节点标签 / Node label
            width: 画布宽度 / Canvas width
            height: 画布高度 / Canvas height
        """
        if 0 <= y < height and 0 <= x < width:
            canvas[y][x] = "*"
        # 绘制标签（在节点右侧）/ Draw label (to the right of the node)
        for i, ch in enumerate(label):
            lx = x + 2 + i
            if 0 <= y < height and 0 <= lx < width:
                canvas[y][lx] = ch

    def _draw_line(
        self, canvas: list[list[str]],
        x1: int, y1: int, x2: int, y2: int,
        width: int, height: int,
    ) -> None:
        """
        在画布上绘制连线（Bresenham算法简化版）
        Draw line on canvas (simplified Bresenham's algorithm)

        Args:
            canvas: 画布 / Canvas
            x1, y1: 起点坐标 / Start coordinates
            x2, y2: 终点坐标 / End coordinates
            width: 画布宽度 / Canvas width
            height: 画布高度 / Canvas height
        """
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy, 1)

        for i in range(steps + 1):
            t = i / steps
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            if 0 <= y < height and 0 <= x < width:
                if canvas[y][x] == " ":
                    canvas[y][x] = "."

    @staticmethod
    def _shorten_path(path: str, max_len: int) -> str:
        """
        缩短文件路径 / Shorten file path

        Args:
            path: 文件路径 / File path
            max_len: 最大长度 / Maximum length

        Returns:
            缩短后的路径 / Shortened path
        """
        if len(path) <= max_len:
            return path
        # 保留文件名和部分路径 / Keep filename and part of path
        basename = os.path.basename(path)
        if len(basename) >= max_len:
            return "..." + basename[-(max_len - 3):]
        available = max_len - len(basename) - 3
        parts = path.replace("\\", "/").split("/")
        if len(parts) <= 1:
            return basename[:max_len]
        return "..." + "/".join(parts[-2:])[-available:] + "/" + basename[-(max_len - available - 4):]


class StatsVisualizer:
    """
    统计信息可视化器 / Statistics visualizer

    以格式化文本展示依赖统计信息。
    Displays dependency statistics as formatted text.
    """

    def __init__(self, graph: DependencyGraph) -> None:
        """
        初始化统计可视化器 / Initialize stats visualizer

        Args:
            graph: 依赖图 / Dependency graph
        """
        self.graph = graph

    def render(self) -> str:
        """
        渲染统计信息 / Render statistics

        Returns:
            统计信息字符串 / Statistics string
        """
        stats = self.graph.get_statistics()
        lines: list[str] = []

        lines.append(f"依赖统计 / Dependency Statistics ({self.graph.base_path})")
        lines.append("=" * 60)

        # 基本信息 / Basic information
        lines.append("")
        lines.append(f"  文件数量 / File count:          {stats['file_count']}")
        lines.append(f"  内部依赖数 / Internal deps:     {stats['dependency_count']}")
        lines.append(f"  外部依赖数 / External deps:     {stats['external_dependency_count']}")
        lines.append(f"  循环依赖数 / Cycles:            {stats['cycle_count']}")
        lines.append(f"  最大依赖深度 / Max depth:       {stats['max_dependency_depth']}")

        # 语言分布 / Language distribution
        lines.append("")
        lines.append("  语言分布 / Language distribution:")
        for lang, count in sorted(stats["language_distribution"].items(), key=lambda x: -x[1]):
            bar_len = min(count * 2, 30)
            bar = "#" * bar_len
            lines.append(f"    {lang:<12} {count:>4}  {bar}")

        # 被依赖最多的文件 / Most depended-upon file
        if stats["most_depended_file"]:
            lines.append("")
            lines.append(f"  最被依赖文件 / Most depended file:")
            lines.append(f"    {stats['most_depended_file']}")

        # 循环依赖详情 / Cycle details
        cycles = self.graph.detect_cycles()
        if cycles:
            lines.append("")
            lines.append(f"  循环依赖详情 / Cycle details:")
            for i, cycle in enumerate(cycles[:10], 1):
                cycle_str = " -> ".join(cycle)
                if len(cycle_str) > 70:
                    cycle_str = cycle_str[:67] + "..."
                lines.append(f"    {i}. {cycle_str}")
            if len(cycles) > 10:
                lines.append(f"    ... 还有 {len(cycles) - 10} 个循环 / ... {len(cycles) - 10} more cycles")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
