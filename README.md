# SmartRename

**Cross-platform batch file renaming — simple, powerful, reversible.**

[English](docs/README.md) | [中文](docs/README_CN.md)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-lightgrey.svg)]()

## Quick Start

```bash
# Install
pip install smartrename

# Preview files
smartrename preview ~/Downloads

# Rename with sequence numbers
smartrename run ~/Downloads --mode sequence

# Undo last operation
smartrename undo
```

## Features

- 6 renaming modes: sequence, date, replace, lowercase, uppercase, clean
- Preview before execution
- Automatic conflict resolution
- **Full undo support** — never lose your original filenames
- Cross-platform: macOS, Windows, Linux

## Documentation

- [Full Documentation (English)](docs/README.md)
- [完整文档 (中文)](docs/README_CN.md)

## License

MIT License — Free to use, modify, and distribute.

---

**Made by [Francisezhang](https://github.com/Francisezhang)**