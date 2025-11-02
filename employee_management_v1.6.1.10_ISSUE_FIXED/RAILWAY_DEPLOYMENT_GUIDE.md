# 🚀 Railway.app部署完整指南

## 员工管理系统 v1.6.1.10 - 生产环境部署

### 📋 部署准备

#### 系统特性
- ✅ **自定义域名**: www.chinapkac.com
- ✅ **多用户并发登录**: 支持多人同时登录
- ✅ **生产环境配置**: 安全加密、静态文件处理
- ✅ **自动数据库迁移**: 无需手动操作
- ✅ **SSL证书**: 自动配置HTTPS

---

## 🎯 部署步骤

### 步骤1: 准备Railway.app账号

1. **注册Railway.app**
   - 访问 [railway.app](https://railway.app)
   - 使用GitHub账号登录（推荐）
   - 完成账号验证

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 如果没有GitHub仓库，选择 "Empty Project"

### 步骤2: 上传代码

**方法1: 直接上传（推荐）**
```bash
# 1. 创建新目录
mkdir employee-management-deploy
cd employee-management-deploy

# 2. 解压项目文件
tar -xzf ../employee_management_v1.6.1.10_ISSUE_FIXED.tar.gz

# 3. 创建Git仓库
git init
git add .
git commit -m "Initial commit"

# 4. 推送到GitHub
# 在GitHub创建新仓库 'employee-management'
git remote add origin https://github.com/your-username/employee-management.git
git push -u origin main
```

**方法2: Railway.app直接部署**
1. 在Railway.app点击 "Deploy from GitHub repo"
2. 选择你的代码仓库
3. Railway会自动检测Django应用

### 步骤3: 配置环境变量

在Railway.app项目设置中，添加以下环境变量：

```bash
# Django设置
DJANGO_SETTINGS_MODULE=employee_management.settings_production
SECRET_KEY=your-secret-key-here-change-this
DEBUG=False

# 允许的主机（自定义域名）
ALLOWED_HOSTS=chinapkac.railway.app,www.chinapkac.com,chinapkac.com

# 数据库（使用Railway默认PostgreSQL）
DATABASE_URL=railway-postgres://...

# 邮件设置（可选）
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 步骤4: 部署启动

Railway.app会自动：
1. 检测Django应用
2. 安装依赖包 (requirements.txt)
3. 运行数据库迁移
4. 收集静态文件
5. 启动应用

### 步骤5: 配置自定义域名

1. **购买域名**
   - 访问阿里云、腾讯云等
   - 购买: chinapkac.com

2. **DNS配置**
   ```
   类型: CNAME
   主机: www
   记录值: chinapkac.railway.app
   TTL: 600
   ```

3. **Railway域名配置**
   - 项目设置 → Domains
   - 添加域名: www.chinapkac.com
   - 按提示配置DNS

---

## 🔧 自动化部署脚本

运行以下脚本进行自动化部署：

```bash
# 1. 执行部署脚本
python deploy_production.py

# 2. 验证部署
python -c "
import requests
response = requests.get('https://chinapkac.railway.app')
print(f'Status: {response.status_code}')
print(f'Content Length: {len(response.content)}')
"
```

---

## 📊 部署验证

### 功能测试清单

- [ ] **首页访问**: https://chinapkac.railway.app
- [ ] **登录功能**: 使用创建的用户账号登录
- [ ] **多用户测试**: 同时打开多个浏览器窗口测试
- [ ] **管理后台**: https://chinapkac.railway.app/admin
- [ ] **员工管理**: 创建、编辑员工信息
- [ ] **请假管理**: 提交、审批请假申请
- [ ] **报告管理**: 上传、查看报告
- [ ] **位置跟踪**: 签到、签退功能
- [ ] **紧急管理**: 发送紧急通知

### 默认测试账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 超级管理员 | admin | password123 | 所有权限 |
| 区域经理 | manager | password123 | 查看区域报告 |
| 任务区经理 | taskmanager | password123 | 管理任务区 |
| 普通员工 | employee | password123 | 基础功能 |

---

## 🌐 自定义域名配置

### DNS记录设置

在域名管理面板添加：

```dns
# www子域名
记录类型: CNAME
主机记录: www
记录值: chinapkac.railway.app
TTL: 600

# 根域名
记录类型: CNAME
主机记录: @
记录值: chinapkac.railway.app  
TTL: 600
```

### 验证自定义域名

配置完成后，测试以下地址：

- https://www.chinapkac.com (WWW版本)
- https://chinapkac.railway.app (Railway版本)

---

## 🛠️ 故障排除

### 常见问题

**1. 部署失败**
```bash
# 检查日志
railway logs

# 常见解决方案
# - 检查requirements.txt
# - 验证环境变量
# - 确认数据库连接
```

**2. 域名不生效**
- 等待DNS传播（最多48小时）
- 检查DNS记录是否正确
- 验证Railway域名配置

**3. SSL证书问题**
- Railway自动处理，等待15分钟
- 检查DNS记录是否指向Railway
- 确认域名配置正确

**4. 数据库连接问题**
- 检查DATABASE_URL环境变量
- 验证数据库服务状态
- 查看Railway日志

---

## 📈 性能优化

### 数据库优化
```python
# 生产环境数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': os.environ['DATABASE_PORT'],
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'max_connections': 20,
        },
    }
}
```

### 缓存配置
```python
# 使用Redis缓存（Railway支持）
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

## 📞 技术支持

### 监控和维护

**Railway.app监控**
- 访问控制台查看应用状态
- 设置告警通知
- 监控数据库连接数

**应用监控**
```python
# 添加健康检查端点
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'version': '1.6.1.10',
        'database': 'connected'
    })
```

### 备份策略

**数据库备份**
```bash
# 手动备份
railway run python manage.py dumpdata > backup.json

# 自动备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
railway run python manage.py dumpdata > backup_${DATE}.json
```

---

## ✅ 部署完成检查清单

- [ ] Railway.app账号注册完成
- [ ] 代码上传并部署成功
- [ ] 环境变量配置正确
- [ ] 数据库迁移完成
- [ ] 静态文件收集成功
- [ ] 管理员账号可登录
- [ ] 所有用户角色功能正常
- [ ] 自定义域名DNS配置完成
- [ ] SSL证书生效
- [ ] 多人并发登录测试通过

---

**🎉 恭喜！你的员工管理系统已成功部署到生产环境！**

**访问地址**: 
- 临时: https://chinapkac.railway.app
- 自定义: https://www.chinapkac.com (DNS配置后)

**管理后台**: https://www.chinapkac.com/admin
