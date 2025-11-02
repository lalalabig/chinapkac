# Render.com 部署指南
## PostgreSQL 数据库 + Django 项目

### 📋 迁移概览

**已完成的准备工作：**
- ✅ 数据库配置从 SQLite 迁移到 PostgreSQL
- ✅ 添加 PostgreSQL 依赖包（psycopg2-binary）
- ✅ 配置 WhiteNoise（静态文件服务）
- ✅ 创建 Render 部署配置文件
- ✅ 准备数据库迁移脚本

**迁移过程：**
将项目数据库从 SQLite 迁移到 PostgreSQL，以便在 Render.com 免费版部署。

---

## 🚀 Render 部署步骤

### 步骤 1：创建 Render 账户
1. 访问 [Render.com](https://render.com)
2. 使用 GitHub 账户登录

### 步骤 2：创建 PostgreSQL 数据库
1. 在 Render Dashboard 中，点击 "New" → "PostgreSQL Database"
2. 配置数据库信息：
   - **Name**: `employee-management-db`
   - **Database**: 选择免费版即可
3. 点击 "Create Database"
4. **重要**：记录以下信息（将在部署 Web Service 时使用）：
   - `DATABASE_HOST`（数据库主机）
   - `DATABASE_PORT`（数据库端口，通常为 5432）
   - `DATABASE_NAME`（数据库名）
   - `DATABASE_USER`（数据库用户名）
   - `DATABASE_PASSWORD`（数据库密码）

### 步骤 3：部署 Web Service
1. 在 Render Dashboard 中，点击 "New" → "Web Service"
2. 选择 "Build and deploy from a Git repository"
3. 连接您的 GitHub 仓库
4. 或者选择 "Use a public repository" → 输入仓库 URL

**服务配置：**
- **Name**: `employee-management`
- **Region**: 选择就近的区域（如 Singapore）
- **Branch**: `main` 或 `master`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn employee_management.wsgi --log-file - --timeout 120`

### 步骤 4：配置环境变量
在 Web Service 设置中添加以下环境变量：

**必需的环境变量：**
```
DEBUG=False
SECRET_KEY=your-super-secret-key-here-32-chars-min
DATABASE_NAME=<步骤2中记录的数据库名>
DATABASE_USER=<步骤2中记录的用户名>
DATABASE_PASSWORD=<步骤2中记录的密码>
DATABASE_HOST=<步骤2中记录的主机>
DATABASE_PORT=5432
```

**可选环境变量：**
```
AMAP_API_KEY=your-amap-api-key-here
TENGENG_SMS_APP_ID=your-sms-app-id
TENGENG_SMS_APP_KEY=your-sms-app-key
```

**⚠️ 重要提示：**
- `SECRET_KEY` 必须至少 32 个字符
- 确保 `DEBUG=False` 在生产环境
- 数据库连接信息必须与步骤2中创建的数据库匹配

### 步骤 5：触发部署
1. 点击 "Create Web Service"
2. Render 会自动构建和部署您的应用
3. 部署完成后，您将获得一个 URL，如：`https://employee-management.onrender.com`

---

## 🔧 数据库迁移

### 本地测试迁移（推荐）
在部署前，您可以在本地测试数据库迁移：

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **创建本地 PostgreSQL 数据库**（可选）：
   ```bash
   createdb employee_management_test
   ```

3. **设置环境变量**：
   ```bash
   export DATABASE_NAME=employee_management_test
   export DATABASE_USER=your_user
   export DATABASE_PASSWORD=your_password
   export DATABASE_HOST=localhost
   export DATABASE_PORT=5432
   export SECRET_KEY=local-test-secret-key-at-least-32-characters
   export DEBUG=True
   ```

4. **运行迁移脚本**：
   ```bash
   python migrate_to_postgresql.py
   ```

### 自动迁移
Render 部署后，如果数据库为空，会自动运行迁移脚本创建所有表和初始数据。

---

## ✅ 部署验证

### 测试步骤：
1. **访问应用**：访问 Render 提供的 URL
2. **管理员登录**：
   - URL: `https://your-app.onrender.com/admin`
   - 用户名: `admin`
   - 密码: `password123`

3. **功能测试**：
   - 用户登录/退出
   - 部门管理
   - 员工管理
   - 任务分配
   - 请假管理

### 预期结果：
- ✅ 应用正常访问
- ✅ 所有页面正常加载
- ✅ 数据库连接成功
- ✅ 管理员登录正常

---

## 🔧 故障排除

### 常见问题：

**1. 数据库连接失败**
```
django.db.utils.OperationalError: could not connect to server
```
**解决方案：**
- 检查环境变量配置是否正确
- 确认数据库已创建并处于运行状态
- 验证网络连接（Render 自动配置）

**2. 静态文件无法加载**
**解决方案：**
- 静态文件使用 WhiteNoise 自动处理
- 检查 `STATIC_ROOT` 和 `STATIC_URL` 配置
- 确保 `whitenoise` 在 `INSTALLED_APPS` 中

**3. 迁移失败**
**解决方案：**
- 运行数据库迁移脚本：`python migrate_to_postgresql.py`
- 检查权限配置
- 确保数据库为空或清理冲突数据

**4. 启动命令错误**
**解决方案：**
- 确保 `Procfile` 存在且内容为：`web: gunicorn employee_management.wsgi --log-file - --timeout 120`
- 检查 Gunicorn 版本：`pip install gunicorn`

---

## 📊 性能优化

### Render 免费版限制：
- **应用休眠**：15分钟无访问后进入休眠
- **内存限制**：512MB
- **CPU限制**：共享CPU
- **数据库连接**：最多20个并发连接

### 优化建议：
- 启用 Django 缓存机制
- 优化静态文件加载
- 使用 Redis 进行会话存储（可选）

---

## 🎯 自定义域名配置

如果需要配置自定义域名（如 www.chinapkac.com）：

1. 在 Render Dashboard 中打开您的 Web Service
2. 进入 "Settings" 页面
3. 找到 "Custom Domains" 部分
4. 添加您的域名
5. 按 Render 指示配置 DNS 记录

---

## 📞 技术支持

如遇到部署问题，请检查：
1. Render 日志（Dashboard → Service → Logs）
2. 环境变量配置
3. 数据库连接状态
4. 依赖包安装情况

**项目信息：**
- 项目名称：Employee Management System
- 版本：v1.6.1.6 (PostgreSQL)
- 框架：Django 4.2.7
- 数据库：PostgreSQL
- 部署平台：Render.com

---

*该指南适用于从 MySQL/SQLite 迁移到 PostgreSQL 的 Django 项目部署*