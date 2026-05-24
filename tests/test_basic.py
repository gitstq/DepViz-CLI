"""
DepViz-CLI 基础测试 / DepViz-CLI basic tests

测试各语言解析器、依赖图构建、循环检测等核心功能。
Tests core functionality: language parsers, graph building, cycle detection, etc.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# 确保可以导入项目模块 / Ensure project modules can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from depviz.parsers.python import PythonParser
from depviz.parsers.javascript import JavaScriptParser
from depviz.parsers.golang import GolangParser
from depviz.parsers.rust import RustParser
from depviz.parsers.java import JavaParser
from depviz.graph import DependencyGraph, build_graph
from depviz.utils import detect_language, scan_files, should_exclude_dir, normalize_path
from depviz.visualizer import TreeVisualizer, StatsVisualizer, RingVisualizer


class TestUtils(unittest.TestCase):
    """工具函数测试 / Utility function tests"""

    def test_detect_language_python(self) -> None:
        """测试Python语言检测 / Test Python language detection"""
        self.assertEqual(detect_language("test.py"), "python")
        self.assertEqual(detect_language("test.pyw"), "python")

    def test_detect_language_javascript(self) -> None:
        """测试JavaScript/TypeScript语言检测 / Test JS/TS language detection"""
        self.assertEqual(detect_language("test.js"), "javascript")
        self.assertEqual(detect_language("test.ts"), "javascript")
        self.assertEqual(detect_language("test.jsx"), "javascript")
        self.assertEqual(detect_language("test.tsx"), "javascript")

    def test_detect_language_golang(self) -> None:
        """测试Go语言检测 / Test Go language detection"""
        self.assertEqual(detect_language("main.go"), "golang")

    def test_detect_language_rust(self) -> None:
        """测试Rust语言检测 / Test Rust language detection"""
        self.assertEqual(detect_language("lib.rs"), "rust")

    def test_detect_language_java(self) -> None:
        """测试Java语言检测 / Test Java language detection"""
        self.assertEqual(detect_language("App.java"), "java")

    def test_detect_language_unknown(self) -> None:
        """测试未知语言 / Test unknown language"""
        self.assertIsNone(detect_language("readme.md"))
        self.assertIsNone(detect_language("data.txt"))

    def test_should_exclude_dir(self) -> None:
        """测试目录排除 / Test directory exclusion"""
        self.assertTrue(should_exclude_dir("node_modules"))
        self.assertTrue(should_exclude_dir("venv"))
        self.assertTrue(should_exclude_dir("__pycache__"))
        self.assertTrue(should_exclude_dir(".git"))
        self.assertTrue(should_exclude_dir("target"))
        self.assertFalse(should_exclude_dir("src"))
        self.assertFalse(should_exclude_dir("lib"))

    def test_should_exclude_dir_custom(self) -> None:
        """测试自定义目录排除 / Test custom directory exclusion"""
        self.assertTrue(should_exclude_dir("my_dir", {"my_dir"}))
        self.assertFalse(should_exclude_dir("src", {"my_dir"}))

    def test_normalize_path(self) -> None:
        """测试路径标准化 / Test path normalization"""
        result = normalize_path("/home/user/project/src/main.py", "/home/user/project")
        self.assertEqual(result, "src/main.py")


class TestPythonParser(unittest.TestCase):
    """Python解析器测试 / Python parser tests"""

    def setUp(self) -> None:
        """设置解析器 / Set up parser"""
        self.parser = PythonParser()

    def test_simple_import(self) -> None:
        """测试简单import / Test simple import"""
        code = "import os\nimport sys\n"
        deps = self.parser.parse("test.py", code)
        self.assertIn("os", deps)
        self.assertIn("sys", deps)

    def test_from_import(self) -> None:
        """测试from...import / Test from...import"""
        code = "from pathlib import Path\nfrom collections import defaultdict\n"
        deps = self.parser.parse("test.py", code)
        self.assertIn("pathlib", deps)
        self.assertIn("collections", deps)

    def test_relative_import_ignored(self) -> None:
        """测试相对导入被忽略 / Test relative imports are ignored"""
        code = "from . import utils\nfrom ..core import engine\n"
        deps = self.parser.parse("test.py", code)
        self.assertEqual(len(deps), 0)

    def test_import_with_alias(self) -> None:
        """测试带别名的import / Test import with alias"""
        code = "import numpy as np\nimport pandas as pd\n"
        deps = self.parser.parse("test.py", code)
        self.assertIn("numpy", deps)
        self.assertIn("pandas", deps)

    def test_import_in_string_ignored(self) -> None:
        """测试字符串中的import被忽略 / Test import in strings is ignored"""
        code = 'x = "import os"\ny = """import sys"""\n'
        deps = self.parser.parse("test.py", code)
        self.assertEqual(len(deps), 0)

    def test_comment_import_ignored(self) -> None:
        """测试注释中的import被忽略 / Test import in comments is ignored"""
        code = "# import os\nx = 1\n"
        deps = self.parser.parse("test.py", code)
        self.assertEqual(len(deps), 0)


class TestJavaScriptParser(unittest.TestCase):
    """JavaScript/TypeScript解析器测试 / JS/TS parser tests"""

    def setUp(self) -> None:
        """设置解析器 / Set up parser"""
        self.parser = JavaScriptParser()

    def test_require(self) -> None:
        """测试require() / Test require()"""
        code = 'const fs = require("fs");\nconst path = require("path");\n'
        deps = self.parser.parse("test.js", code)
        self.assertIn("fs", deps)
        self.assertIn("path", deps)

    def test_import_from(self) -> None:
        """测试import...from / Test import...from"""
        code = 'import React from "react";\nimport { useState } from "react";\n'
        deps = self.parser.parse("test.jsx", code)
        self.assertIn("react", deps)

    def test_dynamic_import(self) -> None:
        """测试动态import() / Test dynamic import()"""
        code = 'const mod = import("lodash");\n'
        deps = self.parser.parse("test.js", code)
        self.assertIn("lodash", deps)

    def test_export_from(self) -> None:
        """测试export...from / Test export...from"""
        code = 'export { foo } from "./bar";\n'
        deps = self.parser.parse("test.js", code)
        # 相对路径会被过滤 / Relative paths are filtered
        self.assertEqual(len(deps), 0)


class TestGolangParser(unittest.TestCase):
    """Go解析器测试 / Go parser tests"""

    def setUp(self) -> None:
        """设置解析器 / Set up parser"""
        self.parser = GolangParser()

    def test_single_import(self) -> None:
        """测试单行import / Test single-line import"""
        code = 'import "fmt"\n'
        deps = self.parser.parse("main.go", code)
        self.assertIn("fmt", deps)

    def test_multi_import(self) -> None:
        """测试多行import / Test multi-line import"""
        code = 'import (\n\t"fmt"\n\t"os"\n\t"strings"\n)\n'
        deps = self.parser.parse("main.go", code)
        self.assertIn("fmt", deps)
        self.assertIn("os", deps)
        self.assertIn("strings", deps)

    def test_aliased_import(self) -> None:
        """测试带别名的import / Test aliased import"""
        code = 'import myfmt "fmt"\n'
        deps = self.parser.parse("main.go", code)
        self.assertIn("fmt", deps)


class TestRustParser(unittest.TestCase):
    """Rust解析器测试 / Rust parser tests"""

    def setUp(self) -> None:
        """设置解析器 / Set up parser"""
        self.parser = RustParser()

    def test_use_statement(self) -> None:
        """测试use语句 / Test use statement"""
        code = "use std::collections::HashMap;\nuse std::fs;\n"
        deps = self.parser.parse("main.rs", code)
        self.assertIn("std", deps)

    def test_use_with_braces(self) -> None:
        """测试带花括号的use / Test use with braces"""
        code = "use std::io::{self, Read, Write};\n"
        deps = self.parser.parse("main.rs", code)
        self.assertIn("std", deps)

    def test_crate_use(self) -> None:
        """测试crate::前缀的use / Test crate:: prefixed use"""
        code = "use crate::utils::helper;\n"
        deps = self.parser.parse("main.rs", code)
        self.assertIn("utils", deps)

    def test_self_super_ignored(self) -> None:
        """测试self::和super::被忽略 / Test self:: and super:: are ignored"""
        code = "use self::local;\nuse super::parent;\n"
        deps = self.parser.parse("main.rs", code)
        self.assertEqual(len(deps), 0)


class TestJavaParser(unittest.TestCase):
    """Java解析器测试 / Java parser tests"""

    def setUp(self) -> None:
        """设置解析器 / Set up parser"""
        self.parser = JavaParser()

    def test_import_class(self) -> None:
        """测试类导入 / Test class import"""
        code = "import java.util.List;\nimport java.util.ArrayList;\n"
        deps = self.parser.parse("App.java", code)
        self.assertIn("java.util.List", deps)
        self.assertIn("java.util.ArrayList", deps)

    def test_wildcard_import(self) -> None:
        """测试通配符导入 / Test wildcard import"""
        code = "import java.util.*;\n"
        deps = self.parser.parse("App.java", code)
        self.assertIn("java.util.*", deps)

    def test_static_import(self) -> None:
        """测试静态导入 / Test static import"""
        code = "import static java.lang.Math.PI;\n"
        deps = self.parser.parse("App.java", code)
        self.assertIn("java.lang.Math.PI", deps)


class TestDependencyGraph(unittest.TestCase):
    """依赖图测试 / Dependency graph tests"""

    def test_empty_graph(self) -> None:
        """测试空图 / Test empty graph"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = DependencyGraph(tmpdir)
            self.assertEqual(graph.file_count, 0)
            self.assertEqual(graph.dependency_count, 0)
            self.assertEqual(len(graph.detect_cycles()), 0)

    def test_add_dependency(self) -> None:
        """测试添加依赖 / Test adding dependency"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = DependencyGraph(tmpdir)
            graph.add_dependency("a.py", "b.py")
            graph.add_dependency("a.py", "c.py")
            self.assertEqual(len(graph.get_dependencies("a.py")), 2)
            self.assertEqual(len(graph.get_dependents("b.py")), 1)

    def test_no_duplicate_edges(self) -> None:
        """测试不重复添加边 / Test no duplicate edges"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = DependencyGraph(tmpdir)
            graph.add_dependency("a.py", "b.py")
            graph.add_dependency("a.py", "b.py")
            self.assertEqual(len(graph.get_dependencies("a.py")), 1)

    def test_cycle_detection(self) -> None:
        """测试循环依赖检测 / Test cycle detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = DependencyGraph(tmpdir)
            graph.add_dependency("a.py", "b.py")
            graph.add_dependency("b.py", "c.py")
            graph.add_dependency("c.py", "a.py")
            cycles = graph.detect_cycles()
            self.assertTrue(len(cycles) > 0)

    def test_no_cycle(self) -> None:
        """测试无循环依赖 / Test no cycle"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = DependencyGraph(tmpdir)
            graph.add_dependency("a.py", "b.py")
            graph.add_dependency("a.py", "c.py")
            graph.add_dependency("b.py", "d.py")
            cycles = graph.detect_cycles()
            self.assertEqual(len(cycles), 0)

    def test_to_json(self) -> None:
        """测试JSON导出 / Test JSON export"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = DependencyGraph(tmpdir)
            graph.add_dependency("a.py", "b.py")
            json_str = graph.to_json()
            data = json.loads(json_str)
            self.assertIn("dependencies", data)
            self.assertIn("statistics", data)

    def test_statistics(self) -> None:
        """测试统计信息 / Test statistics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = DependencyGraph(tmpdir)
            graph.add_dependency("a.py", "b.py")
            graph.add_dependency("a.py", "c.py")
            stats = graph.get_statistics()
            self.assertEqual(stats["file_count"], 3)
            self.assertEqual(stats["dependency_count"], 2)


class TestBuildGraph(unittest.TestCase):
    """依赖图构建测试 / Dependency graph building tests"""

    def test_build_python_project(self) -> None:
        """测试构建Python项目依赖图 / Test building Python project graph"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件 / Create test files
            os.makedirs(os.path.join(tmpdir, "pkg"))
            with open(os.path.join(tmpdir, "main.py"), "w") as f:
                f.write("from pkg import utils\nimport os\n")
            with open(os.path.join(tmpdir, "pkg", "__init__.py"), "w") as f:
                f.write("")
            with open(os.path.join(tmpdir, "pkg", "utils.py"), "w") as f:
                f.write("import json\n")

            graph = build_graph(tmpdir)
            self.assertTrue(graph.file_count >= 2)

    def test_build_empty_dir(self) -> None:
        """测试构建空目录 / Test building empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = build_graph(tmpdir)
            self.assertEqual(graph.file_count, 0)

    def test_nonexistent_path(self) -> None:
        """测试不存在的路径 / Test nonexistent path"""
        with self.assertRaises(FileNotFoundError):
            build_graph("/nonexistent/path/that/does/not/exist")


class TestVisualizers(unittest.TestCase):
    """可视化器测试 / Visualizer tests"""

    def _create_test_graph(self, tmpdir: str) -> DependencyGraph:
        """创建测试用依赖图 / Create test dependency graph"""
        graph = DependencyGraph(tmpdir)
        graph.add_dependency("main.py", "utils.py")
        graph.add_dependency("main.py", "config.py")
        graph.add_dependency("utils.py", "helpers.py")
        return graph

    def test_tree_visualizer(self) -> None:
        """测试树形可视化 / Test tree visualization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = self._create_test_graph(tmpdir)
            viz = TreeVisualizer(graph)
            output = viz.render()
            self.assertIn("main.py", output)
            self.assertIn("utils.py", output)

    def test_stats_visualizer(self) -> None:
        """测试统计可视化 / Test stats visualization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = self._create_test_graph(tmpdir)
            viz = StatsVisualizer(graph)
            output = viz.render()
            self.assertIn("4", output)  # 4 files
            self.assertIn("3", output)  # 3 dependencies

    def test_ring_visualizer(self) -> None:
        """测试环形图可视化 / Test ring visualization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph = self._create_test_graph(tmpdir)
            viz = RingVisualizer(graph)
            output = viz.render()
            self.assertTrue(len(output) > 0)


class TestScanFiles(unittest.TestCase):
    """文件扫描测试 / File scanning tests"""

    def test_scan_python_files(self) -> None:
        """测试扫描Python文件 / Test scanning Python files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建Python文件 / Create Python files
            with open(os.path.join(tmpdir, "a.py"), "w") as f:
                f.write("import os\n")
            os.makedirs(os.path.join(tmpdir, "sub"))
            with open(os.path.join(tmpdir, "sub", "b.py"), "w") as f:
                f.write("import sys\n")

            files = scan_files(tmpdir)
            self.assertEqual(len(files), 2)

    def test_scan_excludes_dirs(self) -> None:
        """测试扫描排除目录 / Test scanning with excluded directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建正常文件 / Create normal files
            with open(os.path.join(tmpdir, "a.py"), "w") as f:
                f.write("import os\n")
            # 创建排除目录中的文件 / Create files in excluded directories
            os.makedirs(os.path.join(tmpdir, "venv", "lib"))
            with open(os.path.join(tmpdir, "venv", "lib", "b.py"), "w") as f:
                f.write("import sys\n")
            os.makedirs(os.path.join(tmpdir, "__pycache__"))
            with open(os.path.join(tmpdir, "__pycache__", "c.py"), "w") as f:
                f.write("import json\n")

            files = scan_files(tmpdir)
            self.assertEqual(len(files), 1)
            self.assertTrue(files[0].endswith("a.py"))

    def test_scan_nonexistent(self) -> None:
        """测试扫描不存在的路径 / Test scanning nonexistent path"""
        with self.assertRaises(FileNotFoundError):
            scan_files("/nonexistent/path")

    def test_scan_file_not_dir(self) -> None:
        """测试扫描文件而非目录 / Test scanning file instead of directory"""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"import os\n")
            f.flush()
            with self.assertRaises(NotADirectoryError):
                scan_files(f.name)
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
