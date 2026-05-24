"""
工具函数模块 / Utility functions module

提供文件扫描、路径处理、语言检测等通用工具函数。
Provides common utility functions for file scanning, path handling, language detection, etc.
"""

import os
import re
from pathlib import Path
from typing import Optional, Set


# 默认排除的目录列表 / Default excluded directories
DEFAULT_EXCLUDE_DIRS: Set[str] = {
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    ".hg",
    ".svn",
    "dist",
    "build",
    ".tox",
    ".eggs",
    "*.egg-info",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "target",       # Rust/Java build output
    "out",          # General build output
    ".gradle",
    ".idea",
    ".vscode",
    "vendor",       # Go vendor directory
    "third_party",
}

# 文件扩展名到语言的映射 / File extension to language mapping
EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".go": "golang",
    ".rs": "rust",
    ".java": "java",
}

# 支持的语言列表 / Supported languages
SUPPORTED_LANGUAGES: Set[str] = set(EXTENSION_LANGUAGE_MAP.values())


def should_exclude_dir(dir_name: str, exclude_dirs: Optional[Set[str]] = None) -> bool:
    """
    判断目录是否应该被排除 / Check if a directory should be excluded

    Args:
        dir_name: 目录名称 / Directory name
        exclude_dirs: 自定义排除目录集合 / Custom excluded directories set

    Returns:
        bool: 是否应该排除 / Whether to exclude
    """
    dirs = DEFAULT_EXCLUDE_DIRS | (exclude_dirs or set())
    return dir_name in dirs


def detect_language(file_path: str) -> Optional[str]:
    """
    根据文件扩展名检测编程语言 / Detect programming language by file extension

    Args:
        file_path: 文件路径 / File path

    Returns:
        语言名称或None / Language name or None
    """
    ext = Path(file_path).suffix.lower()
    return EXTENSION_LANGUAGE_MAP.get(ext)


def scan_files(
    root_path: str,
    exclude_dirs: Optional[Set[str]] = None,
    verbose: bool = False,
) -> list[str]:
    """
    递归扫描目录，收集所有支持语言的源文件
    Recursively scan directory and collect all source files of supported languages

    Args:
        root_path: 根目录路径 / Root directory path
        exclude_dirs: 自定义排除目录集合 / Custom excluded directories set
        verbose: 是否显示详细输出 / Whether to show verbose output

    Returns:
        文件路径列表 / List of file paths
    """
    root = Path(root_path)
    if not root.exists():
        raise FileNotFoundError(f"路径不存在: {root_path} / Path not found: {root_path}")
    if not root.is_dir():
        raise NotADirectoryError(f"不是目录: {root_path} / Not a directory: {root_path}")

    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # 过滤排除的目录 / Filter excluded directories
        dirnames[:] = [
            d for d in dirnames
            if not should_exclude_dir(d, exclude_dirs)
        ]

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            lang = detect_language(file_path)
            if lang is not None:
                files.append(file_path)
                if verbose:
                    print(f"  [SCAN] {file_path} ({lang})")

    return files


def normalize_path(file_path: str, base_path: str) -> str:
    """
    将文件路径标准化为相对于基础路径的格式
    Normalize file path relative to a base path

    Args:
        file_path: 文件绝对路径 / Absolute file path
        base_path: 基础路径 / Base path

    Returns:
        标准化后的相对路径 / Normalized relative path
    """
    try:
        rel = os.path.relpath(file_path, base_path)
        return rel.replace(os.sep, "/")
    except ValueError:
        # 在不同驱动器上时回退到文件名 / Fallback to filename on different drives
        return os.path.basename(file_path)


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小 / Format file size

    Args:
        size_bytes: 字节数 / Number of bytes

    Returns:
        格式化后的字符串 / Formatted string
    """
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
