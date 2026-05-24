"""
CLI入口模块 / CLI entry module

作为 `python -m depviz` 的入口点。
Entry point for `python -m depviz`.
"""

import sys

from depviz.cli import create_parser, run_command


def main() -> int:
    """
    主入口函数 / Main entry function

    Returns:
        退出码 / Exit code
    """
    parser = create_parser()
    args = parser.parse_args()
    return run_command(args)


if __name__ == "__main__":
    sys.exit(main())
