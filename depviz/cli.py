"""
CLI命令定义模块 / CLI command definition module

使用argparse定义DepViz-CLI的所有子命令和参数。
Uses argparse to define all subcommands and arguments for DepViz-CLI.
"""

import argparse
import sys
from typing import Optional

from depviz import __version__
from depviz.graph import build_graph
from depviz.visualizer import RingVisualizer, StatsVisualizer, TreeVisualizer


def create_parser() -> argparse.ArgumentParser:
    """
    创建CLI参数解析器 / Create CLI argument parser

    Returns:
        配置好的ArgumentParser实例 / Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="depviz",
        description="DepViz-CLI - 轻量级终端代码依赖关系可视化引擎\n"
                    "Lightweight terminal code dependency visualization engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "使用示例 / Examples:\n"
            "  depviz scan ./src          扫描目录并显示依赖树\n"
            "  depviz cycle ./src         检测循环依赖\n"
            "  depviz stats ./src         显示依赖统计\n"
            "  depviz export ./src -f json  导出JSON格式\n"
            "  depviz ring ./src          显示环形依赖图\n"
        ),
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"DepViz-CLI v{__version__}",
    )

    # 通用参数 / Common arguments
    common_args = argparse.ArgumentParser(add_help=False)
    common_args.add_argument(
        "--exclude", "-e",
        type=str,
        default="",
        help="排除的目录（逗号分隔）/ Excluded directories (comma-separated)",
    )
    common_args.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="显示详细输出 / Show verbose output",
    )

    # 子命令 / Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        title="可用命令 / Available commands",
        metavar="COMMAND",
    )

    # scan 命令 / scan command
    scan_parser = subparsers.add_parser(
        "scan",
        parents=[common_args],
        help="扫描目录并显示依赖树 / Scan directory and show dependency tree",
        description="递归扫描目录，解析文件依赖关系，以树形结构展示\n"
                    "Recursively scan directory, parse file dependencies, display as tree",
    )
    scan_parser.add_argument(
        "path",
        type=str,
        help="要扫描的目录路径 / Directory path to scan",
    )
    scan_parser.add_argument(
        "--depth", "-d",
        type=int,
        default=5,
        help="树形显示最大深度 (默认: 5) / Max tree depth (default: 5)",
    )
    scan_parser.add_argument(
        "--show-external",
        action="store_true",
        default=False,
        help="显示外部依赖 / Show external dependencies",
    )

    # cycle 命令 / cycle command
    cycle_parser = subparsers.add_parser(
        "cycle",
        parents=[common_args],
        help="检测循环依赖 / Detect circular dependencies",
        description="使用DFS算法检测项目中的循环依赖\n"
                    "Use DFS algorithm to detect circular dependencies in the project",
    )
    cycle_parser.add_argument(
        "path",
        type=str,
        help="要扫描的目录路径 / Directory path to scan",
    )

    # stats 命令 / stats command
    stats_parser = subparsers.add_parser(
        "stats",
        parents=[common_args],
        help="显示依赖统计 / Show dependency statistics",
        description="显示项目依赖关系的统计信息\n"
                    "Show statistics of project dependency relationships",
    )
    stats_parser.add_argument(
        "path",
        type=str,
        help="要扫描的目录路径 / Directory path to scan",
    )

    # export 命令 / export command
    export_parser = subparsers.add_parser(
        "export",
        parents=[common_args],
        help="导出依赖数据 / Export dependency data",
        description="将依赖关系数据导出为指定格式\n"
                    "Export dependency data to specified format",
    )
    export_parser.add_argument(
        "path",
        type=str,
        help="要扫描的目录路径 / Directory path to scan",
    )
    export_parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["json"],
        default="json",
        help="输出格式 (默认: json) / Output format (default: json)",
    )
    export_parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径 (默认输出到stdout) / Output file path (default: stdout)",
    )

    # ring 命令 / ring command
    ring_parser = subparsers.add_parser(
        "ring",
        parents=[common_args],
        help="显示环形依赖图 / Show ring dependency chart",
        description="以ASCII环形图展示文件间的依赖关系\n"
                    "Display file dependencies as ASCII ring chart",
    )
    ring_parser.add_argument(
        "path",
        type=str,
        help="要扫描的目录路径 / Directory path to scan",
    )
    ring_parser.add_argument(
        "--width", "-w",
        type=int,
        default=80,
        help="环形图宽度 (默认: 80) / Ring chart width (default: 80)",
    )
    ring_parser.add_argument(
        "--height",
        type=int,
        default=40,
        help="环形图高度 (默认: 40) / Ring chart height (default: 40)",
    )

    return parser


def _parse_exclude_dirs(exclude_str: str) -> Optional[set[str]]:
    """
    解析排除目录字符串 / Parse exclude directories string

    Args:
        exclude_str: 逗号分隔的目录字符串 / Comma-separated directory string

    Returns:
        目录集合或None / Directory set or None
    """
    if not exclude_str.strip():
        return None
    return {d.strip() for d in exclude_str.split(",") if d.strip()}


def run_command(args: argparse.Namespace) -> int:
    """
    执行CLI命令 / Execute CLI command

    Args:
        args: 解析后的命令行参数 / Parsed command-line arguments

    Returns:
        退出码 (0=成功, 1=错误) / Exit code (0=success, 1=error)
    """
    try:
        if args.command is None:
            # 没有子命令时显示帮助 / Show help when no subcommand
            create_parser().print_help()
            return 0

        exclude_dirs = _parse_exclude_dirs(getattr(args, "exclude", ""))
        verbose = getattr(args, "verbose", False)

        if args.command == "scan":
            return _cmd_scan(args, exclude_dirs, verbose)
        elif args.command == "cycle":
            return _cmd_cycle(args, exclude_dirs, verbose)
        elif args.command == "stats":
            return _cmd_stats(args, exclude_dirs, verbose)
        elif args.command == "export":
            return _cmd_export(args, exclude_dirs, verbose)
        elif args.command == "ring":
            return _cmd_ring(args, exclude_dirs, verbose)
        else:
            print(f"未知命令: {args.command} / Unknown command: {args.command}", file=sys.stderr)
            return 1

    except FileNotFoundError as e:
        print(f"错误: {e} / Error: {e}", file=sys.stderr)
        return 1
    except NotADirectoryError as e:
        print(f"错误: {e} / Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n操作已取消 / Operation cancelled", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"意外错误: {e} / Unexpected error: {e}", file=sys.stderr)
        return 1


def _cmd_scan(
    args: argparse.Namespace,
    exclude_dirs: Optional[set[str]],
    verbose: bool,
) -> int:
    """
    执行scan命令 / Execute scan command

    Args:
        args: 命令参数 / Command arguments
        exclude_dirs: 排除目录 / Excluded directories
        verbose: 详细模式 / Verbose mode

    Returns:
        退出码 / Exit code
    """
    graph = build_graph(args.path, exclude_dirs, verbose)
    visualizer = TreeVisualizer(graph)
    output = visualizer.render(
        max_depth=args.depth,
        show_external=args.show_external,
    )
    print(output)
    return 0


def _cmd_cycle(
    args: argparse.Namespace,
    exclude_dirs: Optional[set[str]],
    verbose: bool,
) -> int:
    """
    执行cycle命令 / Execute cycle command

    Args:
        args: 命令参数 / Command arguments
        exclude_dirs: 排除目录 / Excluded directories
        verbose: 详细模式 / Verbose mode

    Returns:
        退出码 / Exit code
    """
    graph = build_graph(args.path, exclude_dirs, verbose)
    cycles = graph.detect_cycles()

    print(f"循环依赖检测 / Circular Dependency Detection")
    print(f"路径: {args.path}")
    print("=" * 60)

    if not cycles:
        print("  未检测到循环依赖 / No circular dependencies detected")
        print("  项目依赖结构健康 / Project dependency structure is healthy")
    else:
        print(f"  检测到 {len(cycles)} 个循环依赖 / {len(cycles)} cycle(s) detected:")
        print()
        for i, cycle in enumerate(cycles, 1):
            cycle_str = " -> ".join(cycle)
            print(f"  循环 {i} / Cycle {i}:")
            print(f"    {cycle_str}")
            print()

    print("=" * 60)
    return 1 if cycles else 0


def _cmd_stats(
    args: argparse.Namespace,
    exclude_dirs: Optional[set[str]],
    verbose: bool,
) -> int:
    """
    执行stats命令 / Execute stats command

    Args:
        args: 命令参数 / Command arguments
        exclude_dirs: 排除目录 / Excluded directories
        verbose: 详细模式 / Verbose mode

    Returns:
        退出码 / Exit code
    """
    graph = build_graph(args.path, exclude_dirs, verbose)
    visualizer = StatsVisualizer(graph)
    output = visualizer.render()
    print(output)
    return 0


def _cmd_export(
    args: argparse.Namespace,
    exclude_dirs: Optional[set[str]],
    verbose: bool,
) -> int:
    """
    执行export命令 / Execute export command

    Args:
        args: 命令参数 / Command arguments
        exclude_dirs: 排除目录 / Excluded directories
        verbose: 详细模式 / Verbose mode

    Returns:
        退出码 / Exit code
    """
    graph = build_graph(args.path, exclude_dirs, verbose)

    if args.format == "json":
        output = graph.to_json()
    else:
        print(f"不支持的格式: {args.format} / Unsupported format: {args.format}", file=sys.stderr)
        return 1

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"已导出到: {args.output} / Exported to: {args.output}")
        except IOError as e:
            print(f"写入文件失败: {e} / Failed to write file: {e}", file=sys.stderr)
            return 1
    else:
        print(output)

    return 0


def _cmd_ring(
    args: argparse.Namespace,
    exclude_dirs: Optional[set[str]],
    verbose: bool,
) -> int:
    """
    执行ring命令 / Execute ring command

    Args:
        args: 命令参数 / Command arguments
        exclude_dirs: 排除目录 / Excluded directories
        verbose: 详细模式 / Verbose mode

    Returns:
        退出码 / Exit code
    """
    graph = build_graph(args.path, exclude_dirs, verbose)
    visualizer = RingVisualizer(graph)
    output = visualizer.render(width=args.width, height=args.height)
    print(output)
    return 0
