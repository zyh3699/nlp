#!/bin/bash

echo "🚀 启动 Paper2Agent Web 界面"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv ../.venv"
    exit 1
fi

# Activate virtual environment
echo "📦 激活虚拟环境..."
source ../.venv/bin/activate

# Install dependencies
echo "📥 检查依赖..."
pip install -q -r requirements.txt

# Check if installation successful
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖检查完成"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 启动 Web 服务器..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "访问地址: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the Flask app
python app.py
