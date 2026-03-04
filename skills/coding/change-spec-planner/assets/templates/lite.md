---
id: {{ID}}
title: {{TITLE}}
type: {{TYPE}}
level: lite
status: planned
review_required: false
created_at: {{DATE}}
related_issue: {{RELATED_ISSUE}}
---

# 背景
[用 2-4 句话说明当前问题或改进诉求。]

# 目标
- [列出 1-2 个完成后必须达成的结果。]

# 非目标
- [明确本次不做什么，防止范围蔓延。]

# 流程 / 行为
- [若没有流程变化，写“无流程变化”。]

```mermaid
flowchart LR
    A["触发"] --> B["当前或新行为"]
    B --> C["预期结果"]
```

# 文件计划
| 状态 | 层级 | 文件 | 计划变更 |
| --- | --- | --- | --- |
| confirmed | view | `path/to/file` | [说明该文件为何需要修改] |
| suspected | test | `path/to/test` | [说明为何可能需要补充覆盖] |

# 实现说明
- Approach: [简述实现方式。]
- Dependencies: [若无新增或变更依赖，写“None”。]
- Constraints: [列出必须遵守的边界或兼容性要求。]

# 验证计划
| 类型 | 步骤 | 预期结果 |
| --- | --- | --- |
| command | `[command]` | [应通过什么检查或输出什么结果] |
| manual | [手工验证路径] | [可见结果] |

# 风险 / 回滚
- Risk: [主要实现风险]
- Rollback: [如何安全回滚]

# 未决问题 / 假设
- [若无未决问题，写“None”。]

# 执行确认
- [ ] 文档内容已确认，可开始实现
- [ ] 如需修改，先更新本文件再执行

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
