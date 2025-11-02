#!/usr/bin/env python3
"""
Railway.app 自动化部署脚本
员工管理系统 v1.6.1.10 - Railway 部署
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description=""):
    """执行命令并处理错误"""
    print(f"🔄 {description}")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ 命令执行成功")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def check_prerequisites():
    """检查部署前置条件"""
    print("🔍 检查部署前置条件...")
    
    # 检查 Railway CLI 是否安装
    try:
        result = subprocess.run("railway --version", shell=True, check=True, capture_output=True)
        print("✅ Railway CLI 已安装")
        print(f"版本: {result.stdout.strip()}")
    except:
        print("❌ Railway CLI 未安装")
        print("请先安装 Railway CLI:")
        print("npm install -g @railway/cli")
        return False
    
    # 检查是否在项目目录中
    if not Path("Procfile").exists():
        print("❌ 未找到 Procfile 文件")
        print("请确保在项目根目录中运行此脚本")
        return False
    
    # 检查关键文件
    required_files = ["requirements.txt", "Procfile", "deploy_production.py"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少文件: {file}")
            return False
    
    print("✅ 所有前置条件检查通过")
    return True

def setup_railway():
    """设置 Railway 项目"""
    print("🔧 设置 Railway 项目...")
    
    # 检查是否已登录
    if not run_command("railway whoami", "检查 Railway 登录状态"):
        print("请先登录 Railway:")
        run_command("railway login", "登录 Railway")
    
    # 创建或连接到项目
    if not run_command("railway link", "连接 Railway 项目"):
        print("创建新项目...")
        if not run_command("railway create", "创建 Railway 项目"):
            print("❌ 项目创建失败，请手动创建")
            return False
    
    return True

def deploy_to_railway():
    """部署到 Railway"""
    print("🚀 开始部署到 Railway...")
    
    # 安装依赖并部署
    commands = [
        ("railway up", "上传和部署应用"),
        ("railway logs --follow", "查看部署日志"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"❌ 部署步骤失败: {description}")
            return False
    
    return True

def post_deployment():
    """部署后处理"""
    print("📋 部署后配置...")
    
    # 获取项目信息
    result = subprocess.run("railway status", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 部署成功!")
        print("=" * 50)
        print("🎉 员工管理系统已成功部署到 Railway!")
        print("=" * 50)
        print("📱 访问地址: 检查 Railway 控制台")
        print("🔧 管理后台: {your_url}/admin")
        print("📧 默认管理员账号: admin")
        print("🔑 默认密码: password123")
        print("=" * 50)
        print("⚠️  重要提醒:")
        print("1. 部署后请立即修改所有默认密码")
        print("2. 测试所有功能是否正常工作")
        print("3. 考虑配置自定义域名 www.chinapkac.com")
        print("4. 设置定期备份策略")
    else:
        print("❌ 部署状态检查失败")

def main():
    """主函数"""
    print("=" * 60)
    print("🛠️  Railway.app 自动化部署脚本")
    print("📦 员工管理系统 v1.6.1.10")
    print("=" * 60)
    
    # 检查前置条件
    if not check_prerequisites():
        print("❌ 前置条件检查失败，部署终止")
        sys.exit(1)
    
    # 设置 Railway
    if not setup_railway():
        print("❌ Railway 设置失败，部署终止")
        sys.exit(1)
    
    # 执行部署
    if not deploy_to_railway():
        print("❌ 部署失败")
        sys.exit(1)
    
    # 部署后处理
    post_deployment()

if __name__ == "__main__":
    main()