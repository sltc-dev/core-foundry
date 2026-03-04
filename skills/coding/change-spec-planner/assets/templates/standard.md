---
id: {{ID}}
title: {{TITLE}}
type: {{TYPE}}
level: standard
status: planned
review_required: true
created_at: {{DATE}}
related_issue: {{RELATED_ISSUE}}
---

# 背景
[说明业务/技术背景、当前差距以及本次变更必要性。]

# 目标
- [目标 1]
- [目标 2]

# 非目标
- [明确列出不在本次范围内的事项。]

# 用户流程
```mermaid
flowchart LR
    A["入口"] --> B["主操作"]
    B --> C["状态变化"]
    C --> D["结果"]
```

# 变更计划
- [模块或行为变更 1]
- [模块或行为变更 2]
- [测试、可观测性或文档变更]

# 文件计划
| 状态 | 层级 | 文件 | 计划变更 |
| --- | --- | --- | --- |
| confirmed | view | `path/to/view` | [说明该文件为何需要修改] |
| confirmed | component | `path/to/component` | [说明该文件为何需要修改] |
| suspected | service | `path/to/service` | [说明为何可能需要修改] |

# 数据 / 契约影响
- Persisted data: [None / 描述变更]
- API contract: [None / 描述变更]
- Shared state: [None / 描述变更]
- External boundary: [None / 描述与后端或服务协作]

# 约束
- [目录、兼容性或架构约束]
- [必须复用或必须保持不变的边界]

# 验证计划
| 类型 | 步骤 | 预期结果 |
| --- | --- | --- |
| command | `[command]` | [应通过的检查] |
| command | `[command]` | [应通过的检查] |
| manual | [手工验证路径] | [可见结果] |

# 风险 / 回滚
- Risk: [风险 1]
- Risk: [风险 2]
- Rollback: [回滚路径]

# 未决问题 / 假设
- [未决问题或假设 1]
- [未决问题或假设 2]

# 评审结论
- [ ] 范围可接受
- [ ] 风险已理解
- [ ] 验证计划充分
- [ ] 用户已明确确认，允许开始实现

# 实施结果
- [实现后填写。]

# 实际变更文件
| 文件 | 实际变更 |
| --- | --- |
| `path/to/file` | [实现后填写。] |

# 偏离计划说明
- [若与计划一致，写“None”。]

# 验证结果
- [列出实际执行过的命令与手工验证项。]
