# 员工管理系统 v1.6.1.5 修复说明

## 版本信息
- **版本号**: v1.6.1.5
- **修复日期**: 2025-11-02
- **修复内容**: 仪表盘统计、历史记录查看、Excel导出、筛选功能、报告下载优化

---

## 修复问题总览

### 1. ✅ 仪表盘统计数据显示不正确
**问题描述**：
- 用户的请假申请已批准，但"我的请假申请"页面顶部统计卡片全部显示为0
- 应该显示实际的申请数量统计

**根本原因**：
- `my_applications`视图函数只传递了分页对象，没有计算统计数据
- 模板引用了不存在的变量（`total_count`、`pending_count`等）

**修复方案**：
1. 修改`leave_management/views.py`中的`my_applications`函数
2. 添加统计数据计算逻辑：
   - `total_count`: 总申请数
   - `pending_count`: 待审批数量（PENDING_TASK_AREA + PENDING_HEAD）
   - `approved_count`: 已批准数量
   - `rejected_count`: 已拒绝数量
3. 修改`templates/leave_management/my_applications.html`模板
4. 使用正确的变量名替换原来的`applications.total_count`等

**影响文件**：
- `leave_management/views.py` (第22-56行)
- `templates/leave_management/my_applications.html` (第36-98行)

---

### 2. ✅ 申请请假页面缺少历史记录入口
**问题描述**：
- 用户在"申请请假"页面看不到以前提交的记录
- 需要返回导航菜单才能查看历史记录，不够方便

**修复方案**：
1. 在`apply_leave.html`页面标题旁边添加"查看历史记录"按钮
2. 点击按钮跳转到`my_applications`页面
3. 使用Bootstrap样式保持界面一致性

**影响文件**：
- `templates/leave_management/apply_leave.html` (第50-62行)

**用户体验提升**：
- 用户可以在申请页面直接查看历史记录
- 减少了导航步骤，提高操作效率

---

### 3. ✅ 导出Excel功能报错（MergedCell错误）
**问题描述**：
- 点击"导出记录"按钮时出现`AttributeError: 'MergedCell' object has no attribute 'column_letter'`错误
- 导致Excel文件无法生成

**根本原因**：
- 在调整列宽时，代码尝试访问合并单元格（MergedCell）的`column_letter`属性
- 合并单元格对象没有这个属性，导致报错
- 问题出在第466-476行的列宽调整逻辑

**修复方案**：
1. 导入`MergedCell`类用于类型检查
2. 使用列索引（col_idx）和`get_column_letter`函数获取列字母
3. 在遍历单元格时，跳过`MergedCell`类型的单元格
4. 添加异常处理，确保即使某些单元格有问题也不会中断导出

**技术细节**：
```python
from openpyxl.cell import MergedCell
from openpyxl.utils import get_column_letter

for col_idx, col in enumerate(ws.columns, 1):
    column_letter = get_column_letter(col_idx)
    for cell in col:
        # 跳过合并单元格
        if isinstance(cell, MergedCell):
            continue
        # 计算列宽...
```

**影响文件**：
- `leave_management/views.py` (第465-485行)

---

### 4. ✅ 超级管理员缺少筛选功能
**问题描述**：
- 超级管理员在请假管理仪表盘中看到所有数据，数据量大时不便查找
- 缺少按任务区或员工姓名筛选的功能

**修复方案**：

#### 后端修改（views.py）：
1. 修改`leave_management_dashboard`视图函数
2. 添加GET参数接收：`task_area`（任务区ID）、`name`（姓名/用户名）
3. 应用筛选条件到查询：
   - 任务区筛选：`applicant__task_area_fk__id=task_area_filter`
   - 姓名筛选：`Q()`查询，支持first_name、last_name、username
4. 获取可用的任务区列表（根据角色权限）
5. 将筛选条件和任务区列表传递给模板

#### 前端修改（dashboard.html）：
1. 在页面标题下方添加筛选表单卡片
2. 两个筛选字段：
   - 下拉框：选择任务区（显示所有可管辖的任务区）
   - 文本框：输入姓名或用户名
3. 两个操作按钮：
   - "筛选"：提交表单应用筛选
   - "重置"：清除筛选条件
4. 保持选中状态（value="{{ name_filter }}"等）

**权限控制**：
- 超级管理员：可以看到所有任务区
- 总部负责人：只能看到管辖的任务区
- 任务区负责人：不显示筛选表单（只能看自己任务区）

**影响文件**：
- `leave_management/views.py` (第342-420行)
- `templates/leave_management/dashboard.html` (第105-160行)

---

### 5. ✅ 报告下载功能优化
**问题描述**：
- 用户反馈"报告上传"功能中下载等功能无法正常工作
- 经检查发现下载功能代码存在，但用户体验不佳

**优化方案**：
1. 在"我的报告"(`my_reports.html`)列表中添加直接下载按钮
2. 用户无需先点击"查看"进入详情页，可以直接下载
3. 保持与其他报告页面的一致性（`manage_reports.html`、`role_based_reports.html`已有下载按钮）

**影响文件**：
- `templates/reports/my_reports.html` (第88-93行)

**功能验证**：
- ✅ 下载视图函数存在（`download_report`）
- ✅ URL路由正确配置（`reports/urls.py`）
- ✅ 权限检查正常（`can_download_report`）
- ✅ 所有报告页面都有下载按钮

---

## 文件修改清单

### 修改的文件（5个）：
1. **leave_management/views.py**
   - `my_applications`函数：添加统计数据计算（第28-38行）
   - `leave_management_dashboard`函数：添加筛选功能（第342-420行）
   - `export_leave_records`函数：修复MergedCell错误（第465-485行）

2. **templates/leave_management/my_applications.html**
   - 修复统计卡片变量名（第43、58、73、88行）

3. **templates/leave_management/apply_leave.html**
   - 添加"查看历史记录"按钮（第53-62行）

4. **templates/leave_management/dashboard.html**
   - 添加筛选表单（第114-160行）

5. **templates/reports/my_reports.html**
   - 添加直接下载按钮（第91-93行）

---

## 部署指南

### 方法一：完整替换（推荐）
```bash
# 1. 备份当前版本
mv employee_management employee_management_backup_$(date +%Y%m%d)

# 2. 解压新版本
unzip employee_management_v1.6.1.5_COMPLETE.zip
# 或
tar -xzf employee_management_v1.6.1.5_COMPLETE.tar.gz

# 3. 重启服务
python manage.py collectstatic --noinput
sudo systemctl restart employee_management
```

### 方法二：仅更新修改的文件
```bash
# 进入项目目录
cd /path/to/employee_management

# 备份要修改的文件
cp leave_management/views.py leave_management/views.py.bak
cp templates/leave_management/my_applications.html templates/leave_management/my_applications.html.bak
cp templates/leave_management/apply_leave.html templates/leave_management/apply_leave.html.bak
cp templates/leave_management/dashboard.html templates/leave_management/dashboard.html.bak
cp templates/reports/my_reports.html templates/reports/my_reports.html.bak

# 从v1.6.1.5包中复制新文件
# （根据实际路径调整）
cp employee_management_v1.6.1.5_COMPLETE/leave_management/views.py leave_management/
cp employee_management_v1.6.1.5_COMPLETE/templates/leave_management/my_applications.html templates/leave_management/
cp employee_management_v1.6.1.5_COMPLETE/templates/leave_management/apply_leave.html templates/leave_management/
cp employee_management_v1.6.1.5_COMPLETE/templates/leave_management/dashboard.html templates/leave_management/
cp employee_management_v1.6.1.5_COMPLETE/templates/reports/my_reports.html templates/reports/

# 重启服务
sudo systemctl restart employee_management
```

---

## 测试验证步骤

### 1. 测试统计数据显示
1. 以普通员工身份登录
2. 访问"我的请假申请"页面
3. 检查顶部4个统计卡片：
   - 总申请数：应显示实际数量
   - 待审批：应显示待审批的数量
   - 已生效：应显示已批准的数量
   - 已拒绝：应显示已拒绝的数量

### 2. 测试历史记录查看
1. 访问"申请请假"页面
2. 点击右上角"查看历史记录"按钮
3. 应该跳转到"我的请假申请"页面并显示历史记录

### 3. 测试Excel导出功能
1. 以任务区负责人/总部负责人/超级管理员身份登录
2. 访问"请假管理仪表盘"
3. 点击"导出记录"按钮
4. 应该成功下载Excel文件，文件中：
   - 标题行正确合并（A1:K1）
   - 所有列宽自动调整
   - 数据完整显示

### 4. 测试筛选功能
1. 以超级管理员身份登录
2. 访问"请假管理仪表盘"
3. 应该看到筛选表单（任务区下拉框 + 姓名搜索框）
4. 测试筛选：
   - 选择某个任务区，点击"筛选"，应该只显示该任务区的数据
   - 输入员工姓名，点击"筛选"，应该只显示匹配的员工
   - 同时使用两个条件筛选
   - 点击"重置"，应该清除筛选条件

### 5. 测试报告下载功能
1. 以普通员工身份登录
2. 上传一份报告
3. 访问"我的报告"页面
4. 在报告列表中应该看到两个按钮：
   - "查看"按钮：进入详情页
   - "下载"按钮：直接下载报告
5. 点击"下载"按钮，应该成功下载文件

---

## 常见问题排查

### Q1: 统计数据仍然显示为0
**可能原因**：
- 模板缓存未清除
- 浏览器缓存未刷新

**解决方法**：
```bash
# 清除Django缓存
python manage.py clear_cache

# 重启服务
sudo systemctl restart employee_management

# 浏览器：强制刷新（Ctrl+F5）
```

### Q2: Excel导出仍然报错
**可能原因**：
- openpyxl版本过旧
- 代码未正确更新

**解决方法**：
```bash
# 检查openpyxl版本
pip show openpyxl

# 如果版本低于3.0，升级
pip install --upgrade openpyxl

# 验证views.py是否正确更新
grep "MergedCell" leave_management/views.py
```

### Q3: 筛选功能不显示
**可能原因**：
- 用户角色不是超级管理员或总部负责人
- 模板条件判断问题

**解决方法**：
1. 确认用户角色：
```python
# 在Django shell中检查
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(username='your_username')
>>> print(user.role)
>>> print(user.role == User.Role.SUPERUSER)
```

2. 检查模板是否更新：
```bash
grep "all_task_areas" templates/leave_management/dashboard.html
```

### Q4: 下载按钮点击无反应
**可能原因**：
- URL路由配置问题
- 权限检查失败

**解决方法**：
1. 检查URL配置：
```bash
grep "download_report" reports/urls.py
```

2. 检查浏览器控制台错误信息

3. 检查Django日志：
```bash
tail -f /path/to/logs/django.log
```

---

## 技术改进点

### 1. 数据统计优化
- 使用Django ORM的`.count()`方法，提高查询效率
- 避免加载完整对象，只统计数量

### 2. 代码健壮性提升
- 添加MergedCell类型检查
- 使用异常处理避免单点失败
- 设置列宽的最小值和最大值限制

### 3. 用户体验改进
- 减少页面跳转次数
- 提供直接下载功能
- 添加筛选功能方便数据查找
- 保持筛选状态

### 4. 性能优化
- 使用Q查询对象进行复杂筛选
- 只查询需要的字段
- 合理使用分页减少数据加载量

---

## 后续建议

### 功能增强：
1. **高级筛选**：
   - 添加日期范围筛选
   - 添加状态筛选（待审批/已批准/已拒绝）
   - 支持多条件组合筛选

2. **导出优化**：
   - 支持导出筛选后的数据
   - 添加PDF格式导出
   - 支持自定义导出字段

3. **批量操作**：
   - 批量审批
   - 批量导出
   - 批量删除（已取消的申请）

### 性能优化：
1. 添加数据库索引：
```python
class LeaveApplication(models.Model):
    # 添加索引
    class Meta:
        indexes = [
            models.Index(fields=['applicant', 'status']),
            models.Index(fields=['leave_start_date', 'leave_end_date']),
        ]
```

2. 使用缓存统计数据（对于不经常变化的数据）

---

## 版本历史

### v1.6.1.5 (2025-11-02)
- ✅ 修复统计数据显示问题
- ✅ 添加历史记录查看入口
- ✅ 修复Excel导出MergedCell错误
- ✅ 添加超级管理员筛选功能
- ✅ 优化报告下载用户体验

### v1.6.1.4 (之前版本)
- 修复请假申请审批功能
- 添加缺失的模板文件
- 完善请假管理仪表盘

---

## 联系支持

如果在部署或使用过程中遇到问题，请提供以下信息：
1. Django版本和Python版本
2. 具体错误信息（截图或日志）
3. 操作步骤
4. 用户角色和权限信息

祝使用愉快！
