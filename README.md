# 🔍 DepViz-CLI

> **Lightweight Terminal Code Dependency Visualization Engine**
> **轻量级终端代码依赖关系可视化引擎**

[简体中文](#简体中文) · [繁體中文](#繁體中文) · [English](#english)

---

<a href="https://github.com/gitstq/DepViz-CLI/stargazers"><img src="https://img.shields.io/github/stars/gitstq/DepViz-CLI?style=social" alt="Stars"></a>
<a href="https://github.com/gitstq/DepViz-CLI/releases"><img src="https://img.shields.io/github/v/release/gitstq/DepViz-CLI?color=blue" alt="Release"></a>
<a href="https://github.com/gitstq/DepViz-CLI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/gitstq/DepViz-CLI" alt="License"></a>
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.8+-green.svg" alt="Python"></a>
<a href="https://github.com/gitstq/DepViz-CLI/issues"><img src="https://img.shields.io/github/issues/gitstq/DepViz-CLI" alt="Issues"></a>

---

## 简体中文

### 🎉 项目介绍

**DepViz-CLI** 是一款轻量级终端代码依赖关系可视化引擎，专为开发者日常项目依赖管理而设计。它能递归扫描项目目录，智能解析代码文件中的 `import`、`require`、`use` 等依赖声明，自动构建完整的依赖关系图谱，并在终端中以直观的**树形视图**和 **ASCII 环形图**进行可视化展示。

**💡 灵感来源**：在日常开发中，随着项目规模增长，模块间的依赖关系日趋复杂。循环依赖、冗余引用等问题难以通过肉眼排查。DepViz-CLI 正是为解决这一痛点而生——无需安装任何第三方依赖，一条命令即可洞察项目依赖全貌。

**🚀 自研差异化亮点**：
- **零外部依赖**：纯 Python 标准库实现，无需 `pip install` 任何第三方包
- **6+ 语言支持**：Python、JavaScript/TypeScript、Go、Rust、Java 一站式覆盖
- **DFS 循环依赖检测**：基于深度优先搜索算法，精准定位循环引用链路
- **双模式可视化**：树形视图 + ASCII 环形图，适配不同分析场景
- **智能排除**：自动跳过 `node_modules`、`venv`、`__pycache__`、`target` 等非源码目录
- **多格式导出**：支持 JSON 格式导出，便于集成到 CI/CD 流水线

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🌐 **多语言解析** | 支持 Python、JavaScript/TypeScript、Go、Rust、Java 六种主流语言 |
| 🔄 **循环依赖检测** | DFS 算法自动检测并高亮循环依赖链路 |
| 🌳 **树形视图** | 以缩进树形结构展示文件间的依赖层级关系 |
| 🎯 **环形依赖图** | ASCII 环形图直观展示模块间的依赖拓扑 |
| 📊 **依赖统计** | 文件数量、内部/外部依赖数、循环依赖数一目了然 |
| 📦 **JSON 导出** | 标准化 JSON 格式输出，便于程序化处理 |
| 🚫 **智能排除** | 自动过滤构建产物、虚拟环境、包管理目录 |
| ⚡ **零依赖运行** | 纯 Python 标准库，开箱即用 |
| 🧪 **完善测试** | 46 个单元测试，覆盖核心功能 |

### 🚀 快速开始

**环境要求**：
- Python 3.8 或更高版本
- 无需任何第三方依赖

**安装**：

```bash
# 克隆仓库
git clone https://github.com/gitstq/DepViz-CLI.git
cd DepViz-CLI

# 安装（开发模式）
pip install -e .
```

**一键运行**：

```bash
# 扫描项目依赖树
depviz scan /path/to/your/project

# 或者直接使用 Python 模块方式运行
python -m depviz scan /path/to/your/project
```

### 📖 详细使用指南

#### 1. 扫描依赖树 🌳

递归扫描指定目录，以树形结构展示文件间的依赖关系：

```bash
# 扫描当前目录
depviz scan .

# 扫描指定路径
depviz scan /path/to/project

# 排除特定目录
depviz scan . --exclude tests,docs
```

**输出示例**：
```
📄 depviz/cli.py
  ├── 📄 depviz/graph.py
  │   ├── 📄 depviz/parsers/__init__.py
  │   └── 📄 depviz/parsers/python.py
  ├── 📄 depviz/visualizer.py
  └── 📄 depviz/utils.py
```

#### 2. 检测循环依赖 🔄

使用 DFS 算法检测项目中的循环依赖：

```bash
depviz cycle /path/to/project
```

**输出示例**：
```
🔄 发现 2 个循环依赖:

  1. module_a.py → module_b.py → module_a.py
  2. utils/config.py → utils/logger.py → utils/config.py
```

#### 3. 查看依赖统计 📊

展示项目依赖关系的统计概览：

```bash
depviz stats /path/to/project
```

#### 4. 导出 JSON 数据 📦

将依赖关系导出为 JSON 格式，便于程序化处理：

```bash
depviz export /path/to/project --format json
```

#### 5. 环形依赖图 🎯

以 ASCII 环形图展示模块间的依赖拓扑关系：

```bash
depviz ring /path/to/project
```

### 💡 设计思路与迭代规划

**设计理念**：
- **极简主义**：零外部依赖，一个文件即可运行
- **开发者友好**：清晰的终端输出，支持管道操作
- **可扩展性**：基于解析器基类的插件化架构，轻松添加新语言支持

**技术选型**：
- Python 标准库 `argparse`：CLI 参数解析
- Python 标准库 `re`：正则表达式匹配依赖声明
- Python 标准库 `os/pathlib`：文件系统遍历
- DFS 算法：有向图环检测

**后续迭代计划**：
- [ ] 支持 C/C++（`#include`）依赖解析
- [ ] 支持 PHP（`use`/`require`）依赖解析
- [ ] 添加 `--depth` 参数限制扫描深度
- [ ] 支持 SVG 格式导出依赖图
- [ ] 集成 pre-commit hook，提交前自动检测循环依赖
- [ ] 添加 Web UI 可视化模式

### 📦 打包与部署指南

本项目为纯 Python 工具库/CLI 工具，无需打包为可执行文件。

**安装使用**：

```bash
# 从 PyPI 安装（发布后）
pip install depviz-cli

# 从源码安装
git clone https://github.com/gitstq/DepViz-CLI.git
cd DepViz-CLI
pip install -e .
```

**兼容环境**：
- Python 3.8+
- Windows / macOS / Linux
- 无需编译，跨平台直接运行

### 🤝 贡献指南

欢迎社区贡献！请遵循以下规范：

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

**提交规范**（Angular Convention）：
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具变更

**Issue 反馈**：请使用 [GitHub Issues](https://github.com/gitstq/DepViz-CLI/issues) 提交 Bug 报告或功能建议。

### 📄 开源协议

本项目基于 [MIT License](https://github.com/gitstq/DepViz-CLI/blob/main/LICENSE) 开源。

---

## 繁體中文

### 🎉 專案介紹

**DepViz-CLI** 是一款輕量級終端程式碼依賴關係視覺化引擎，專為開發者日常專案依賴管理而設計。它能遞迴掃描專案目錄，智慧解析程式碼檔案中的 `import`、`require`、`use` 等依賴宣告，自動建構完整的依賴關係圖譜，並在終端中以直觀的**樹狀檢視**和 **ASCII 環形圖**進行視覺化展示。

**💡 靈感來源**：在日常開發中，隨著專案規模增長，模組間的依賴關係日趨複雜。循環依賴、冗餘引用等問題難以透過肉眼排查。DepViz-CLI 正是為解決這一痛點而生——無需安裝任何第三方依賴，一條命令即可洞察專案依賴全貌。

**🚀 自研差異化亮點**：
- **零外部依賴**：純 Python 標準函式庫實作，無需 `pip install` 任何第三方套件
- **6+ 語言支援**：Python、JavaScript/TypeScript、Go、Rust、Java 一站式覆蓋
- **DFS 循環依賴偵測**：基於深度優先搜尋演算法，精準定位循環引用鏈路
- **雙模式視覺化**：樹狀檢視 + ASCII 環形圖，適配不同分析場景
- **智慧排除**：自動跳過 `node_modules`、`venv`、`__pycache__`、`target` 等非原始碼目錄
- **多格式匯出**：支援 JSON 格式匯出，便於整合到 CI/CD 管線

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🌐 **多語言解析** | 支援 Python、JavaScript/TypeScript、Go、Rust、Java 六種主流語言 |
| 🔄 **循環依賴偵測** | DFS 演算法自動偵測並高亮循環依賴鏈路 |
| 🌳 **樹狀檢視** | 以縮排樹狀結構展示檔案間的依賴層級關係 |
| 🎯 **環形依賴圖** | ASCII 环形圖直觀展示模組間的依賴拓撲 |
| 📊 **依賴統計** | 檔案數量、內部/外部依賴數、循環依賴數一目了然 |
| 📦 **JSON 匯出** | 標準化 JSON 格式輸出，便於程式化處理 |
| 🚫 **智慧排除** | 自動過濾建構產物、虛擬環境、套件管理目錄 |
| ⚡ **零依賴執行** | 純 Python 標準函式庫，開箱即用 |
| 🧪 **完善測試** | 46 個單元測試，覆蓋核心功能 |

### 🚀 快速開始

**環境要求**：
- Python 3.8 或更高版本
- 無需任何第三方依賴

**安裝**：

```bash
# 克隆倉庫
git clone https://github.com/gitstq/DepViz-CLI.git
cd DepViz-CLI

# 安裝（開發模式）
pip install -e .
```

**一鍵執行**：

```bash
# 掃描專案依賴樹
depviz scan /path/to/your/project

# 或直接使用 Python 模組方式執行
python -m depviz scan /path/to/your/project
```

### 📖 詳細使用指南

#### 1. 掃描依賴樹 🌳

遞迴掃描指定目錄，以樹狀結構展示檔案間的依賴關係：

```bash
# 掃描當前目錄
depviz scan .

# 掃描指定路徑
depviz scan /path/to/project

# 排除特定目錄
depviz scan . --exclude tests,docs
```

#### 2. 偵測循環依賴 🔄

使用 DFS 演算法偵測專案中的循環依賴：

```bash
depviz cycle /path/to/project
```

#### 3. 查看依賴統計 📊

展示專案依賴關係的統計概覽：

```bash
depviz stats /path/to/project
```

#### 4. 匯出 JSON 資料 📦

將依賴關係匯出為 JSON 格式，便於程式化處理：

```bash
depviz export /path/to/project --format json
```

#### 5. 環形依賴圖 🎯

以 ASCII 環形圖展示模組間的依賴拓撲關係：

```bash
depviz ring /path/to/project
```

### 💡 設計思路與迭代規劃

**設計理念**：
- **極簡主義**：零外部依賴，一個檔案即可執行
- **開發者友善**：清晰的終端輸出，支援管道操作
- **可擴展性**：基於解析器基類的外掛化架構，輕鬆新增語言支援

**後續迭代計畫**：
- [ ] 支援 C/C++（`#include`）依賴解析
- [ ] 支援 PHP（`use`/`require`）依賴解析
- [ ] 新增 `--depth` 參數限制掃描深度
- [ ] 支援 SVG 格式匯出依賴圖
- [ ] 整合 pre-commit hook，提交前自動偵測循環依賴

### 📦 打包與部署指南

本專案為純 Python 工具庫/CLI 工具，無需打包為可執行檔。

**安裝使用**：

```bash
# 從 PyPI 安裝（發布後）
pip install depviz-cli

# 從原始碼安裝
git clone https://github.com/gitstq/DepViz-CLI.git
cd DepViz-CLI
pip install -e .
```

**相容環境**：
- Python 3.8+
- Windows / macOS / Linux
- 無需編譯，跨平台直接執行

### 🤝 貢獻指南

歡迎社群貢獻！請遵循以下規範：

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feature/your-feature`
3. 提交變更：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

**提交規範**（Angular Convention）：
- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具變更

**Issue 回饋**：請使用 [GitHub Issues](https://github.com/gitstq/DepViz-CLI/issues) 提交 Bug 報告或功能建議。

### 📄 開源協議

本專案基於 [MIT License](https://github.com/gitstq/DepViz-CLI/blob/main/LICENSE) 開源。

---

## English

### 🎉 Introduction

**DepViz-CLI** is a lightweight terminal code dependency visualization engine designed for developers' daily project dependency management. It recursively scans project directories, intelligently parses dependency declarations like `import`, `require`, and `use` in source files, automatically builds a complete dependency graph, and visualizes it in the terminal with intuitive **tree views** and **ASCII ring charts**.

**💡 Inspiration**: As projects grow in scale, inter-module dependency relationships become increasingly complex. Circular dependencies and redundant references are hard to spot manually. DepViz-CLI was born to solve this pain point — zero third-party dependencies required, one command to reveal the full picture of your project's dependencies.

**🚀 Key Differentiators**:
- **Zero External Dependencies**: Pure Python standard library, no `pip install` needed
- **6+ Language Support**: Python, JavaScript/TypeScript, Go, Rust, Java — all in one tool
- **DFS Circular Dependency Detection**: Depth-first search algorithm for pinpointing circular reference chains
- **Dual Visualization Modes**: Tree view + ASCII ring chart for different analysis scenarios
- **Smart Exclusion**: Automatically skips `node_modules`, `venv`, `__pycache__`, `target`, etc.
- **Multi-format Export**: JSON format output for CI/CD pipeline integration

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🌐 **Multi-language Parsing** | Supports Python, JavaScript/TypeScript, Go, Rust, Java |
| 🔄 **Circular Dependency Detection** | DFS algorithm to detect and highlight circular dependency chains |
| 🌳 **Tree View** | Indented tree structure showing file dependency hierarchy |
| 🎯 **Ring Chart** | ASCII ring chart for intuitive dependency topology visualization |
| 📊 **Dependency Statistics** | File count, internal/external dependencies, circular dependencies at a glance |
| 📦 **JSON Export** | Standardized JSON output for programmatic processing |
| 🚫 **Smart Exclusion** | Auto-filters build artifacts, virtual environments, package directories |
| ⚡ **Zero Dependencies** | Pure Python standard library, ready to use out of the box |
| 🧪 **Comprehensive Tests** | 46 unit tests covering core functionality |

### 🚀 Quick Start

**Requirements**:
- Python 3.8 or higher
- No third-party dependencies required

**Installation**:

```bash
# Clone the repository
git clone https://github.com/gitstq/DepViz-CLI.git
cd DepViz-CLI

# Install (development mode)
pip install -e .
```

**Run**:

```bash
# Scan project dependency tree
depviz scan /path/to/your/project

# Or run as Python module
python -m depviz scan /path/to/your/project
```

### 📖 Detailed Usage Guide

#### 1. Scan Dependency Tree 🌳

Recursively scan a directory and display the dependency tree:

```bash
# Scan current directory
depviz scan .

# Scan a specific path
depviz scan /path/to/project

# Exclude specific directories
depviz scan . --exclude tests,docs
```

**Output Example**:
```
📄 depviz/cli.py
  ├── 📄 depviz/graph.py
  │   ├── 📄 depviz/parsers/__init__.py
  │   └── 📄 depviz/parsers/python.py
  ├── 📄 depviz/visualizer.py
  └── 📄 depviz/utils.py
```

#### 2. Detect Circular Dependencies 🔄

Use DFS algorithm to detect circular dependencies in your project:

```bash
depviz cycle /path/to/project
```

**Output Example**:
```
🔄 Found 2 circular dependencies:

  1. module_a.py → module_b.py → module_a.py
  2. utils/config.py → utils/logger.py → utils/config.py
```

#### 3. View Dependency Statistics 📊

Display a statistical overview of your project's dependencies:

```bash
depviz stats /path/to/project
```

#### 4. Export JSON Data 📦

Export dependency relationships in JSON format for programmatic processing:

```bash
depviz export /path/to/project --format json
```

#### 5. Ring Dependency Chart 🎯

Display an ASCII ring chart of module dependency topology:

```bash
depviz ring /path/to/project
```

### 💡 Design Philosophy & Roadmap

**Design Principles**:
- **Minimalism**: Zero external dependencies, single-file execution
- **Developer-Friendly**: Clear terminal output with pipe support
- **Extensibility**: Plugin-based architecture with parser base class for easy language additions

**Tech Stack**:
- Python standard library `argparse`: CLI argument parsing
- Python standard library `re`: Regex matching for dependency declarations
- Python standard library `os/pathlib`: File system traversal
- DFS Algorithm: Directed graph cycle detection

**Roadmap**:
- [ ] C/C++ (`#include`) dependency parsing support
- [ ] PHP (`use`/`require`) dependency parsing support
- [ ] Add `--depth` parameter to limit scan depth
- [ ] SVG format export for dependency graphs
- [ ] pre-commit hook integration for automatic circular dependency detection
- [ ] Web UI visualization mode

### 📦 Packaging & Deployment

This project is a pure Python CLI tool/library — no executable packaging needed.

**Installation**:

```bash
# From PyPI (after publishing)
pip install depviz-cli

# From source
git clone https://github.com/gitstq/DepViz-CLI.git
cd DepViz-CLI
pip install -e .
```

**Compatible Environments**:
- Python 3.8+
- Windows / macOS / Linux
- No compilation required, cross-platform

### 🤝 Contributing

Community contributions are welcome! Please follow these guidelines:

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Submit a **Pull Request**

**Commit Convention** (Angular Convention):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tooling changes

**Issue Reporting**: Please use [GitHub Issues](https://github.com/gitstq/DepViz-CLI/issues) for bug reports or feature suggestions.

### 📄 License

This project is licensed under the [MIT License](https://github.com/gitstq/DepViz-CLI/blob/main/LICENSE).

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
