# Railway.app 快速部署指南

## 📋 前置条件确认
✅ Railway.app 账号已注册并通过 GitHub 登录
✅ 部署包已准备: employee_management_v1.6.1.10_RAILWAY_DEPLOY.tar.gz

## 🚀 快速部署步骤

### 步骤 1: 下载并解压部署包
1. 下载 `employee_management_v1.6.1.10_RAILWAY_DEPLOY.tar.gz` 到本地
2. 解压到任意文件夹，如: `C:\deploy\` 或 `~/deploy/`

### 步骤 2: 安装 Railway CLI
在命令行/终端中执行:
```bash
npm install -g @railway/cli
```

### 步骤 3: 进入项目目录
```bash
cd employee_management_v1.6.1.10_ISSUE_FIXED
```

### 步骤 4: 登录 Railway
```bash
railway login
```
(这会打开浏览器，请授权访问你的 GitHub 账号)

### 步骤 5: 执行部署 (二选一)

#### 选项 A: 使用自动化脚本 (推荐)
```bash
python railway_deploy.py
```

#### 选项 B: 手动部署
```bash
# 1. 创建 Railway 项目
railway create

# 2. 部署应用
railway up

# 3. 查看部署日志
railway logs

# 4. 获取访问地址
railway status
```

### 步骤 6: 获取访问信息
部署成功后，你将在控制台看到类似信息:
```
✅ 部署成功!
📱 访问地址: https://xxxxxx.railway.app
🔧 管理后台: https://xxxxxx.railway.app/admin
📧 管理员账号: admin
🔑 密码: password123
```

## 🧪 测试登录
访问提供的网址，使用以下账号测试:

| 用户角色 | 用户名 | 密码 | 权限 |
|---------|--------|------|------|
| 管理员 | admin | password123 | 完整权限 |
| 部门经理 | manager | password123 | 管理下属员工 |
| 任务区域经理 | taskmanager | password123 | 管理任务区域 |
| 普通员工 | employee | password123 | 基本功能 |

## ⚠️ 重要提醒
1. **立即修改密码**: 部署后请修改所有默认密码
2. **功能测试**: 测试所有模块是否正常工作
3. **数据备份**: 定期备份重要数据
4. **监控运行**: 检查应用运行状态

## 🔧 故障排除

### Railway CLI 登录失败
```bash
railway logout
railway login
```

### 部署失败
```bash
# 查看详细日志
railway logs

# 重新部署
railway up
```

### 无法访问网站
1. 检查 Railway 项目状态
2. 确认域名配置正确
3. 查看应用日志排查错误

## 📞 技术支持
如果遇到问题，请告诉我具体在哪一步遇到问题，我会提供详细解决方案。

---
**部署完成后，你可以使用 https://xxxxxx.railway.app 访问员工管理系统！** 🎉