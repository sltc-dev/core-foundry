---
id: {{ID}}
title: {{TITLE}}
type: {{TYPE}}
level: standard
status: draft
review_required: true
created_at: {{DATE}}
related_issue: {{RELATED_ISSUE}}
---

# 背景
[描述业务背景、现状问题和触发来源。]

# 目标
- [目标 1]
- [目标 2]

# 非目标
- [明确本次不做的范围]

# 用户流程
```mermaid
flowchart LR
    A["入口"] --> B["关键操作"]
    B --> C["中间状态"]
    C --> D["结果"]
```

# 改动点
- [模块 A 的改动]
- [模块 B 的改动]
- [交互或状态变化]

# 涉及文件
| 状态 | 层级 | 文件 | 计划修改 |
| --- | --- | --- | --- |
| confirmed | page | `path/to/file` | [修改原因] |
| confirmed | component | `path/to/component` | [修改原因] |
| suspected | service | `path/to/service` | [待确认原因] |

# 技术方案 / 依赖
- [使用的技术点]
- [新增或升级的包]
- [需要同步的配置、脚本或样式资源]

# 目录与结构约束
- [需要遵循的目录结构]
- [是否允许新增公共组件、工具函数或状态模块]
- [与现有模块边界的关系]

# 数据与接口影响
- 数据结构: [无 / 有，说明字段变化]
- 接口契约: [无 / 有，说明请求或响应变化]
- 云函数或后端联动: [无 / 有，说明影响点]

# 影响范围评估
- UI 页面: [列出页面]
- 共享状态: [列出 store / 缓存 / 本地存储]
- 公共组件: [列出组件]
- 权限 / 登录态: [无 / 有]
- 埋点 / 日志: [无 / 有]
- 测试 / 文档: [需要补充项]

# 验收标准
- [ ] [验收项 1]
- [ ] [验收项 2]

# 风险与回滚
- 风险: [主要风险 1]
- 风险: [主要风险 2]
- 回滚: [回滚方式]

# 待确认问题 / 假设
- [待确认项 1]
- [假设项 1]

# Review Checklist
- [ ] 需求边界已确认
- [ ] 文件范围可接受
- [ ] 风险可接受
- [ ] 可以进入开发

# Implementation Result
- [开发完成后补充]

# Actual Changed Files
- [开发完成后补充]

# Deviation From Plan
- [开发完成后补充；如无，写“无”]

# Verification
- [开发完成后补充]
