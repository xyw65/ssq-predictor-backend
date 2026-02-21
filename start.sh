#!/bin/bash

echo "=========================================="
echo "  智能预测实验室 - 快速启动脚本"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，请先安装Node.js 18+"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动后端
echo "🚀 启动后端服务..."
cd backend

if [ ! -d "venv" ]; then
    echo "  创建Python虚拟环境..."
    python3 -m venv venv
fi

echo "  激活虚拟环境..."
source venv/bin/activate

echo "  安装依赖..."
pip install -r requirements.txt -q

echo "  启动Flask服务..."
python app.py &
BACKEND_PID=$!

cd ..

# 等待后端启动
sleep 3

echo ""
echo "🚀 启动前端服务..."
cd app

if [ ! -d "node_modules" ]; then
    echo "  安装前端依赖..."
    npm install
fi

echo "  启动Vite开发服务器..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "=========================================="
echo "  ✅ 服务已启动！"
echo "=========================================="
echo ""
echo "  前端地址: http://localhost:5173"
echo "  后端地址: http://localhost:5000"
echo ""
echo "  按 Ctrl+C 停止服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
