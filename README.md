# DepViz-CLI

轻量级终端代码依赖关系可视化引擎 / Lightweight terminal code dependency visualization engine

## 功能 / Features

- 支持 6 种语言：Python、JavaScript/TypeScript、Go、Rust、Java
- 依赖树可视化
- 循环依赖检测（DFS 算法）
- ASCII 环形依赖图
- 依赖统计
- JSON 格式导出
- 零外部依赖

## 安装 / Install

```bash
pip install -e .
```

## 使用 / Usage

```bash
# 扫描依赖树
depviz scan <path>

# 检测循环依赖
depviz cycle <path>

# 查看统计信息
depviz stats <path>

# 导出 JSON
depviz export <path> --format json

# 环形依赖图
depviz ring <path>
```
