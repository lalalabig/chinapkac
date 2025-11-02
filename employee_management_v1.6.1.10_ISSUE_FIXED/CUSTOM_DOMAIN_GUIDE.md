# 员工管理系统自定义域名配置指南

## 概述
本指南说明如何为你的员工管理系统配置自定义域名 www.chinapkac.com

## 配置步骤

### 步骤1: 购买域名
1. 访问域名注册商（阿里云、腾讯云、GoDaddy等）
2. 购买域名：chinapkac.com（费用约¥50-100/年）
3. 等待域名注册完成

### 步骤2: 配置DNS解析
1. 登录域名注册商控制面板
2. 找到DNS管理部分
3. 添加以下DNS记录：

```
记录类型: CNAME
主机记录: www
记录值: chinapkac.railway.app
TTL: 600秒

记录类型: CNAME  
主机记录: @
记录值: chinapkac.railway.app
TTL: 600秒
```

### 步骤3: 配置Railway.app自定义域名
1. 访问 Railway.app 控制面板
2. 选择你的员工管理项目
3. 进入 Settings → Domains
4. 点击 "Add Domain"
5. 输入: www.chinapkac.com
6. 点击 "Add Domain"
7. 按照Railway的DNS配置说明操作

### 步骤4: SSL证书
Railway.app 会自动为自定义域名配置 Let's Encrypt SSL证书
该过程需要5-15分钟时间

### 步骤5: Django设置
生产环境设置已包含 www.chinapkac.com 在 ALLOWED_HOSTS 中

## 各平台DNS配置示例

### 阿里云配置
```
记录类型: CNAME
主机记录: www
解析线路: 默认
记录值: chinapkac.railway.app
TTL: 10分钟
```

### 腾讯云配置
```
记录类型: CNAME
主机记录: www
记录值: chinapkac.railway.app
TTL: 600
```

### GoDaddy配置
```
Type: CNAME
Name: www
Value: chinapkac.railway.app
TTL: 1 hour
```

## 验证步骤

完成配置后，请按以下步骤验证：

1. 等待15-30分钟让DNS生效
2. 测试: ping www.chinapkac.com
3. 测试: curl https://www.chinapkac.com
4. 浏览器访问: https://www.chinapkac.com
5. 测试管理后台: https://www.chinapkac.com/admin
6. 确认SSL证书: 检查浏览器锁图标

## 常见问题排查

| 问题 | 解决方案 |
|------|----------|
| 域名不解析 | 检查DNS记录是否正确，等待DNS传播(最多48小时) |
| SSL证书问题 | Railway自动处理，等待15分钟让SSL证书生成 |
| 404错误 | 检查ALLOWED_HOSTS是否包含域名 |
| 重定向问题 | 检查Django的LOGIN_REDIRECT_URL设置 |

## 部署后访问地址

部署完成后，你的系统将可以通过以下地址访问：

- 临时地址: https://chinapkac.railway.app
- 自定义域名: https://www.chinapkac.com (购买域名后)

## 管理员访问

- 管理后台: https://www.chinapkac.com/admin
- 默认管理员账号: admin / password123

## 多用户并发登录

系统支持多人同时登录，不同账号可以同时访问系统功能。

---

**注意**: 自定义域名配置需要大约30分钟到24小时生效，取决于域名注册商。
