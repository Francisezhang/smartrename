# SmartRename

**Batch file renaming for macOS — simple, powerful, reversible.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

SmartRename is a command-line tool for batch renaming files on macOS. It supports 6 renaming patterns with full undo capability through session history.

**Features:**
- 6 renaming modes: sequence, date, replace, lowercase, uppercase, clean
- Preview before execution with rich terminal UI
- Automatic conflict resolution (adds _1, _2 suffixes)
- Full undo support with history tracking
- Recursive directory processing
- Glob pattern filtering

## Installation

```bash
# Quick install
cd smartrename
pip install -e .

# Or with setup script
./setup.sh
```

## Quick Start

```bash
# Preview files
smartrename preview ~/Downloads

# Rename with sequence numbers
smartrename run ~/Downloads --mode sequence

# Add date prefix
smartrename run ~/Downloads --mode date

# Replace text (regex)
smartrename run ~/Downloads --mode replace --find "\d+" --replace-with "NUM" --regex

# Dry run (preview only)
smartrename run ~/Downloads --mode lowercase --dry-run

# Undo last operation
smartrename undo
```

## Commands

### `smartrename preview <directory>`

Preview files in a directory with序号、文件名、大小、修改时间.

Options:
- `-p, --pattern`: Glob pattern (e.g. `*.jpg`)
- `-r, --recursive`: Include subdirectories

### `smartrename run <directory> --mode <mode>`

Rename files using one of 6 modes:

| Mode | Description | Options |
|------|-------------|---------|
| `sequence` | Add序号前缀 (001_, 002_) | `--start`, `--padding` |
| `date` | Add modification date prefix | None |
| `replace` | Replace text | `--find`, `--replace-with`, `--regex` |
| `lowercase` | Convert to lowercase | None |
| `uppercase` | Convert to uppercase | None |
| `clean` | Clean filename | None |

Universal options:
- `-p, --pattern`: Filter by glob pattern
- `-r, --recursive`: Process subdirectories
- `-d, --dry-run`: Preview only
- `-y, --yes`: Skip confirmation

### `smartrename undo [--list] [session_id]`

Undo rename operations:
- `--list`: Show all sessions
- `session_id`: Undo specific session

### `smartrename clean-history`

Clear all history records.

## Examples

```bash
# Rename all JPGs with sequence
smartrename run ~/Photos --mode sequence -p "*.jpg"

# Clean messy filenames
smartrename run ~/Downloads --mode clean --yes

# Add date prefix to documents
smartrename run ~/Documents --mode date -r

# Replace "copy" with nothing
smartrename run ~/Desktop --mode replace --find "copy" --replace-with ""
```

## History

All operations are saved to `~/.smartrename/history.json`. Use `smartrename undo` to revert any session.

## Requirements

- Python 3.9+
- macOS

## License

MIT License — Free to use, modify, and distribute.

---

**Made by [Francisezhang](https://github.com/Francisezhang)**