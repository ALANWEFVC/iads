#!/bin/bash
# IADS 快速启动脚本

echo "🚀 IADS Quick Start"
echo "=================="

# 检查文件
if [ ! -f "iads_main.py" ]; then
    echo "❌ iads_main.py not found"
    exit 1
fi

# 创建日志目录
mkdir -p logs

echo "✅ Starting IADS..."
echo "   Access logs in ./logs/"
echo "   Press Ctrl+C to stop"
echo ""

# 启动
ryu-manager --verbose --observe-links iads_main.py
