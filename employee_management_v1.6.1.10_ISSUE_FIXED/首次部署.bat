@echo off
chcp 65001 >nul
echo ========================================
echo    员工管理系统 - 首次部署
echo    版本: v1.4.0
echo ========================================
echo.
echo ⚠️  重要提示：
echo 1. 如果这是更新部署，请先备份旧的db.sqlite3数据库文件
echo 2. 本脚本将清理无效的任务区数据
echo.
pause
echo.

echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python环境正常
echo.

echo [2/5] 安装依赖包...
if exist requirements.txt (
    pip install -r requirements.txt
    echo ✓ 依赖包安装完成
) else (
    echo ⚠️  未找到requirements.txt，跳过
)
echo.

echo [3/5] 应用数据库迁移...
python manage.py migrate
if errorlevel 1 (
    echo ❌ 数据库迁移失败
    pause
    exit /b 1
)
echo ✓ 数据库迁移完成
echo.

echo [4/5] 清理无效任务区数据...
echo.
if exist cleanup_invalid_task_areas.py (
    python cleanup_invalid_task_areas.py
    echo ✓ 数据清理完成
) else (
    echo ⚠️  未找到清理脚本，跳过此步骤
)
echo.

echo [5/5] 收集静态文件...
if not exist static mkdir static
python manage.py collectstatic --noinput
echo ✓ 静态文件收集完成
echo.

echo ========================================
echo ✅ 部署完成！
echo.
echo 下一步:
echo 1. 运行 start_server.bat 启动服务器
echo 2. 访问 http://127.0.0.1:8000
echo 3. 使用超级管理员账号登录
echo ========================================
echo.
pause