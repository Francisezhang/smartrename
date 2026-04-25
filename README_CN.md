# SmartRename

**跨平台批量文件重命名工具 — 简单、强大、可撤销**

[English](docs/README.md) | [中文](docs/README_CN.md)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-lightgrey.svg)]()

## 快速开始

```bash
# 安装
pip install smartrename

# 预览文件
smartrename preview ~/Downloads

# 序列号重命名
smartrename run ~/Downloads --mode sequence

# 撤销操作
smartrename undo
```

## 功能特点

- 6种重命名模式：序列、日期、替换、小写、大写、清理
- 执行前预览
- 自动处理冲突
- **完全撤销** — 随时恢复原文件名
- 跨平台：macOS、Windows、Linux

## 文档

- [完整文档 (English)](docs/README.md)
- [完整文档 (中文)](docs/README_CN.md)

## 许可证

MIT 许可证 — 免费使用、修改和分发。

---

**由 [Francisezhang](https://github.com/Francisezhang) 开发**