#!/bin/bash
# SmartRename Installation Script
# 智能重命名工具安装脚本

set -e

echo "================================================"
echo "  SmartRename 安装脚本 / Installation Script"
echo "================================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
MIN_VERSION="3.9"

if [ "$(printf '%s\n%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
    echo "❌ Error 错误: Python $MIN_VERSION+ required."
    echo "   当前版本 Current: $PYTHON_VERSION"
    echo ""
    echo "   请安装 Python 3.9+:"
    echo "   brew install python"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected."
echo ""

# Install
echo "📦 Installing SmartRename... / 正在安装..."
pip install -e .

echo ""
echo "================================================"
echo "  ✅ Installation Complete! 安装完成!"
echo "================================================"
echo ""
echo "Quick Start 快速开始:"
echo ""
echo "  smartrename preview ~/Downloads"
echo "  smartrename run ~/Downloads --mode sequence"
echo "  smartrename run ~/Downloads --mode clean --dry-run"
echo ""
echo "For more info 更多信息:"
echo "  smartrename --help"
echo ""
echo "History saved to 历史记录保存在:"
echo "  ~/.smartrename/history.json"
echo ""
echo "================================================"

# Uninstall option
if [ "$1" == "--uninstall" ]; then
    echo ""
    echo "📦 Uninstalling SmartRename... / 正在卸载..."
    pip uninstall smartrename -y
    rm -rf ~/.smartrename
    echo "✅ Uninstalled. 已卸载"
fi