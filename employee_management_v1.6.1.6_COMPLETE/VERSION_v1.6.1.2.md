# 版本信息 v1.6.1.2

## 版本号
v1.6.1.2

## 发布日期
2025-11-02

## 版本类型
🔥 关键修复版本 (Critical Fix)

## 修复内容

### 核心问题
修复了用户登录认证问题，确保所有用户都能正常登录系统。

### 技术细节
1. **问题**: 部分用户密码存储为明文，未经过Django标准加密
2. **影响**: 只有 superuser01 可以登录，其他用户无法通过认证
3. **修复**: 使用 PBKDF2-SHA256 算法重新加密所有用户密码
4. **验证**: 通过自动化测试确认所有用户可正常登录

### 新增工具
- check_users_db.py - 用户信息检查工具
- fix_user_passwords.py - 密码修复工具
- test_login_all_users.py - 登录测试工具
- diagnose_login_issue.py - 问题诊断工具

## 测试状态
✅ 所有 6 个用户账号登录测试通过
✅ 密码加密格式验证通过
✅ Django 认证系统兼容性验证通过

## 升级说明
从 v1.6.1.1 升级到本版本:
1. 替换整个项目目录
2. 或仅替换 db.sqlite3 文件

## 测试账号
所有账号统一密码: 123456

- superuser01 (超级管理员)
- branch_manager01 (任务区负责人)
- test_employee (普通员工)
- test_manager (任务区负责人)
- test_employee_verify (普通员工)
- test_manager_verify (任务区负责人)

## 安全建议
- 生产环境部署前请修改所有默认密码
- 建议实施密码复杂度策略
- 建议添加密码定期更换机制

## 兼容性
- Python: 3.8+
- Django: 4.2.7
- 数据库: SQLite3
- 操作系统: Windows/Linux/macOS

## 已知问题
无

## 下一版本计划
- 添加密码复杂度要求
- 实现密码重置功能
- 添加账号锁定机制
- 增强安全审计日志

---
发布者: MiniMax Agent
