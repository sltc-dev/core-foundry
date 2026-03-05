---
id: {{ID}}
title: {{TITLE}}
type: {{TYPE}}
level: {{LEVEL}}
status: planned
review_required: {{REVIEW_REQUIRED}}
created_at: {{DATE}}
related_issue: {{RELATED_ISSUE}}
---

# 背景
[用 2-4 句话说明当前问题或改进诉求。]

# 目标
- [目标 1]
- [目标 2]

# 非目标
- [明确本次不做什么，防止范围蔓延。]

# 流程 / 行为摘要
- [若无流程变化，写“无流程变化”。]
- [仅在有关键流程变化时添加 Mermaid；若无则不要添加 Mermaid。]

# 文件计划
| 状态 | 层级 | 文件 | 计划变更 |
| --- | --- | --- | --- |
| confirmed | view | `path/to/file` | [说明该文件为何需要修改] |
| suspected | test | `path/to/test` | [说明为何可能需要补充覆盖] |

# 实现说明
- Approach: [简述实现方式。]
- Constraints: [列出边界、兼容性或目录约束。]
- Reuse: [说明必须复用的模块/模式，若无写 None。]

# 验证计划（固定三项）
| 项目 | 命令 | 预期结果 |
| --- | --- | --- |
| eslint | `[例如: corepack yarn lint]` | pass |
| ts/typecheck | `[例如: corepack yarn typecheck]` | pass |
| unit test | `[例如: corepack yarn test:unit]` | pass |

# 风险 / 回滚
- Risk: [主要风险，若 level=lite 且风险极低可写 None。]
- Rollback: [回滚步骤。]

# 未决问题 / 假设
- [若无未决问题，写 None。]

# 执行确认
- [ ] 若 level=lite：用户已明确确认，可开始实现
- [ ] 若 level=risky：人工评审已通过
- [ ] 若 level=risky：用户已明确确认，可开始实现

# 实施结果
- [实现后填写。]

# 实际变更文件
| 文件 | 实际变更 |
| --- | --- |
| `path/to/file` | [实现后填写。] |

# 偏离计划说明
- [若与计划一致，写 None。]

# 验证结果
- eslint: [pass / fail / skip + reason]
- ts/typecheck: [pass / fail / skip + reason]
- unit test: [pass / fail / skip + reason]
