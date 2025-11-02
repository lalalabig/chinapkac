# 版本说明 v1.6.1.5

## 快速信息
- **版本**: v1.6.1.5
- **发布日期**: 2025-11-02
- **修复类型**: Bug修复 + 功能增强
- **修改文件**: 5个
- **新增文件**: 0个

---

## 修复内容速览

| 问题编号 | 问题描述 | 严重程度 | 状态 |
|---------|---------|---------|------|
| #1 | 仪表盘统计数据显示为0 | 高 | ✅ 已修复 |
| #2 | 缺少历史记录查看入口 | 中 | ✅ 已修复 |
| #3 | Excel导出功能报错 | 高 | ✅ 已修复 |
| #4 | 超级管理员缺少筛选功能 | 中 | ✅ 已修复 |
| #5 | 报告下载体验不佳 | 低 | ✅ 已优化 |

---

## 核心修复

### 1. 统计数据修复
**问题**: 已批准的申请不显示在"已生效"统计中  
**修复**: 添加完整的统计数据计算逻辑

### 2. Excel导出修复
**问题**: AttributeError: 'MergedCell' object has no attribute 'column_letter'  
**修复**: 跳过合并单元格，使用列索引获取列字母

### 3. 筛选功能增强
**新增**: 超级管理员和总部负责人可按任务区/姓名筛选数据

---

## 文件对比

### v1.6.1.4 → v1.6.1.5

```
修改的文件:
M  leave_management/views.py              (+41, -14)
M  templates/leave_management/my_applications.html  (+4, -4)
M  templates/leave_management/apply_leave.html      (+8, -2)
M  templates/leave_management/dashboard.html        (+47, -0)
M  templates/reports/my_reports.html                (+3, -0)

新增的文件:
A  FIX_README_v1.6.1.5.md
A  VERSION_v1.6.1.5.md

总计: 5个文件修改, 2个新文档
```

---

## 快速部署

### 最小化部署步骤
```bash
# 1. 备份
cp -r employee_management employee_management.bak

# 2. 替换5个文件
cp v1.6.1.5/leave_management/views.py employee_management/leave_management/
cp v1.6.1.5/templates/leave_management/*.html employee_management/templates/leave_management/
cp v1.6.1.5/templates/reports/my_reports.html employee_management/templates/reports/

# 3. 重启
sudo systemctl restart employee_management
```

### 验证部署
```bash
# 检查统计数据
1. 登录系统 → 我的请假申请 → 查看顶部统计卡片

# 检查导出功能
2. 登录管理员账户 → 请假管理仪表盘 → 点击"导出记录"

# 检查筛选功能
3. 超级管理员登录 → 请假管理仪表盘 → 使用筛选表单
```

---

## 升级注意事项

### 兼容性
✅ **向下兼容**: 是  
✅ **数据库迁移**: 不需要  
✅ **依赖更新**: 不需要

### 风险评估
- **低风险**: 仅修改视图逻辑和模板显示
- **无数据库变更**: 不涉及模型修改
- **可快速回滚**: 保留v1.6.1.4备份即可

---

## 测试检查清单

- [ ] 统计数据正确显示
- [ ] 历史记录按钮可用
- [ ] Excel导出成功
- [ ] 筛选功能正常（超级管理员）
- [ ] 报告直接下载可用

---

## 已知限制

1. 筛选功能仅对超级管理员和总部负责人可见
2. 导出Excel仅包含当前角色可见的数据
3. 统计数据不包含已取消的申请

---

## 下一版本计划

### v1.6.1.6 (计划)
- [ ] 添加日期范围筛选
- [ ] 支持批量审批
- [ ] 添加数据统计图表
- [ ] 优化移动端显示

---

## 文档链接
- 详细修复说明: `FIX_README_v1.6.1.5.md`
- 部署指南: 见FIX_README第二部分
- 测试指南: 见FIX_README第三部分
