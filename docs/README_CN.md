# SmartRename 批量文件重命名工具

**macOS 批量文件重命名工具 — 简单、强大、可撤销**

## 简介

SmartRename 是一个专为 macOS 设计的命令行批量重命名工具。支持 6 种重命名模式，并具有完整的历史记录和撤销功能。

**核心功能：**
- 6 种重命名模式：序号、日期、替换、大小写转换、清理
- 执行前预览，Rich 终端美化显示
- 自动冲突处理（添加 _1、_2 后缀）
- 完整撤销支持，历史记录追踪
- 递归处理子目录
- Glob 模式筛选

## 安装

```bash
# 快速安装
cd smartrename
pip install -e .

# 或使用安装脚本
./setup.sh
```

## 快速上手

```bash
# 预览文件
smartrename preview ~/Downloads

# 添加序号前缀
smartrename run ~/Downloads --mode sequence

# 添加日期前缀
smartrename run ~/Downloads --mode date

# 替换文本（正则）
smartrename run ~/Downloads --mode replace --find "\d+" --replace-with "NUM" --regex

# 仅预览不执行
smartrename run ~/Downloads --mode lowercase --dry-run

# 撤销上次操作
smartrename undo
```

## 命令详解

### `smartrename preview <目录>`

预览目录中的文件，显示序号、文件名、大小、修改时间。

选项：
- `-p, --pattern`: 文件模式（如 `*.jpg`）
- `-r, --recursive`: 包含子目录

### `smartrename run <目录> --mode <模式>`

使用 6 种模式之一重命名文件：

| 模式 | 描述 | 选项 |
|------|------|------|
| `sequence` | 添加序号前缀 (001_, 002_) | `--start`, `--padding` |
| `date` | 添加修改日期前缀 | 无 |
| `replace` | 替换文本 | `--find`, `--replace-with`, `--regex` |
| `lowercase` | 转小写 | 无 |
| `uppercase` | 转大写 | 无 |
| `clean` | 清理文件名 | 无 |

通用选项：
- `-p, --pattern`: 按模式筛选
- `-r, --recursive`: 处理子目录
- `-d, --dry-run`: 仅预览
- `-y, --yes`: 跳过确认

### `smartrename undo [--list] [会话ID]`

撤销重命名操作：
- `--list`: 显示所有会话
- `会话ID`: 撤销特定会话

### `smartrename clean-history`

清空所有历史记录。

## 使用示例

```bash
# 给所有 JPG 图片添加序号
smartrename run ~/Photos --mode sequence -p "*.jpg"

# 清理混乱的文件名
smartrename run ~/Downloads --mode clean --yes

# 给文档添加日期前缀
smartrename run ~/Documents --mode date -r

# 删除文件名中的 "copy"
smartrename run ~/Desktop --mode replace --find "copy" --replace-with ""
```

## 历史记录

所有操作保存在 `~/.smartrename/history.json`。使用 `smartrename undo` 可撤销任意会话。

## 系统要求

- Python 3.9+
- macOS

## 许可证

MIT License — 免费使用、修改和分发。

---

**由 [Francisezhang](https://github.com/Francisezhang) 开发**