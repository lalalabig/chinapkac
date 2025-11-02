#!/bin/bash
echo "========================================"
echo "   员工管理系统 - 快速启动"
echo "   版本: v1.4.0"
echo "========================================"
echo ""

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi
echo "✓ Python环境正常"
echo ""

echo "[2/3] 应用数据库迁移..."
python3 manage.py migrate
if [ $? -ne 0 ]; then
    echo "❌ 数据库迁移失败"
    exit 1
fi
echo "✓ 数据库迁移完成"
echo ""

echo "[3/3] 启动开发服务器..."
echo ""
echo "========================================"
echo "服务器启动成功！"
echo ""
echo "访问地址: http://127.0.0.1:8000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================"
echo ""

python3 manage.py runserver