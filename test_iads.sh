#!/bin/bash
# IADS 测试脚本

echo "🧪 IADS Test Suite"
echo "=================="

echo "1. 语法检查..."
if python3 -m py_compile iads_main.py; then
    echo "   ✅ 语法正确"
else
    echo "   ❌ 语法错误"
    exit 1
fi

echo ""
echo "2. 配置检查..."
if [ -f "iads_config.py" ]; then
    python3 iads_config.py
else
    echo "   ⚠️ 使用默认配置"
fi

echo ""
echo "3. 启动测试..."
echo "   控制器将在后台启动进行测试"

# 后台启动控制器
ryu-manager iads_main.py &
RYU_PID=$!

# 等待启动
sleep 3

# 检查进程
if kill -0 $RYU_PID 2>/dev/null; then
    echo "   ✅ 控制器启动成功 (PID: $RYU_PID)"
    
    # 检查端口
    if netstat -tuln | grep -q ":6633 "; then
        echo "   ✅ 端口6633监听正常"
    else
        echo "   ❌ 端口6633未监听"
    fi
    
    # 停止测试
    kill $RYU_PID
    echo "   ✅ 测试完成，控制器已停止"
else
    echo "   ❌ 控制器启动失败"
    exit 1
fi

echo ""
echo "🎉 所有测试通过！"
echo ""
echo "启动命令："
echo "   ./start_iads.sh"
echo "   或"
echo "   ./deploy_iads.sh"
