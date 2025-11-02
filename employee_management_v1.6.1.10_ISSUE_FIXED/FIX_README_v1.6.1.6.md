# v1.6.1.6 修复说明

## 快速概览

本版本修复了4个问题:

### ✅ 问题1: 审批管理仪表盘筛选报错
**修复**: 添加了类型转换,确保筛选功能正常工作

### ✅ 问题2: 工作报告权限逻辑调整
**修复**: 任务区负责人现在只能查看:
- 本任务区普通员工的报告
- 自己上传的报告

### ✅ 问题3: 工作报告下载文件名优化
**新格式**: `姓名_任务区_时间段_报告类型.扩展名`
**示例**: `张三_华东区_2025-W10_周报.pdf`

### ✅ 问题4: 删除统计报表功能
**删除**: 统计报表视图、URL 和导航链接已全部删除

## 快速部署

### 完整替换（推荐）
```bash
# 1. 备份数据库
cp db.sqlite3 db.sqlite3.backup

# 2. 解压新版本
unzip employee_management_v1.6.1.6_COMPLETE.zip

# 3. 复制数据库
cp db.sqlite3.backup employee_management_v1.6.1.6/db.sqlite3

# 4. 启动
cd employee_management_v1.6.1.6
python manage.py runserver
```

### 文件替换
仅替换以下6个文件后重启:
- `leave_management/views.py`
- `reports/views.py`
- `reports/models.py`
- `dashboard/views.py`
- `dashboard/urls.py`
- `templates/base.html`

## 测试清单
- [ ] 审批管理的任务区筛选功能正常
- [ ] 任务区负责人只能看到普通员工报告
- [ ] 下载报告文件名格式正确
- [ ] 统计报表链接已消失

完整说明请查看 `VERSION_v1.6.1.6.md`
