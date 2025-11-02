#!/bin/bash

# 员工管理系统 v1.6.1.9 启动脚本
# 工作报告筛选功能增强版

echo "========================================"
echo "员工管理系统 v1.6.1.9 启动脚本"
echo "工作报告筛选功能增强版"
echo "========================================"

# 检查是否在正确的目录
if [ ! -f "manage.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "正确的目录包含 manage.py 文件"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查项目依赖..."
if ! command -v uv &> /dev/null; then
    echo "⚠️  警告: uv 工具未找到，尝试使用 pip 安装依赖..."
    pip install -r requirements.txt
else
    echo "✅ uv 工具存在，开始同步依赖..."
    uv sync
fi

# 迁移数据库（如果需要）
echo "🔄 检查数据库迁移..."
if [ ! -f "db.sqlite3" ] || [ ! -s "db.sqlite3" ]; then
    echo "📊 初始化数据库..."
    if command -v uv &> /dev/null; then
        uv run python manage.py migrate
    else
        python manage.py migrate
    fi
else
    echo "✅ 数据库已存在，跳过迁移"
fi

# 启动开发服务器
echo "🚀 启动Django开发服务器..."
echo "访问地址: http://localhost:8000"
echo ""
echo "测试账号:"
echo "  - 超级管理员: admin / admin123"
echo "  - 总部负责人: head_manager_1 / password123" 
echo "  - 任务区负责人: task_manager_1 / password123"
echo ""
echo "新功能:工作报告筛选功能"
echo "  - 所有管理层级可按时间段筛选"
echo "  - 总部负责人和超级管理员可按任务区和姓名筛选"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================"

if command -v uv &> /dev/null; then
    uv run python manage.py runserver 0.0.0.0:8000
else
    python manage.py runserver 0.0.0.0:8000
fi