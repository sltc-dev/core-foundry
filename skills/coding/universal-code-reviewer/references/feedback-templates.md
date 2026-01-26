# 反馈模板

提交 CR 结果时请使用此模板。

## 分类图标
- 🔴 **Blocker (阻断)**: 严重问题、违反"红线"规则、逻辑错误或安全风险。必须修复。
- 🟡 **Suggestion (建议)**: 可读性、可维护性或性能方面的改进。非阻断性。
- 🔵 **Question (疑问)**: 对业务逻辑或意图的确认。

## 审查结果模板
```markdown
# 代码审查总结

## 🔴 Blocker ({blocker_count})
- **[文件名]**: {问题描述}
  - *背景*: 为什么在本项目中这是一个阻断问题。
  - *建议修改*: [代码片段]

## 🟡 Suggestion ({suggestion_count})
- **[文件名]**: {潜在优化点}

## 🔵 Question ({question_count})
- {需要向用户确认的问题}

---
## 🏁 结论
{整体健康度评分与总结}
```

## 证据模式
在指出不一致时，使用此格式：
- "⚠️ 与 `{other_file.ts}` 不一致: 本项目通常使用 `{pattern}`，但 `{current_file.ts}` 使用了 `{wrong_pattern}`。"

## 项目规则定义 (重要)
当定义或更新项目规则 (`rules/{project}.md`) 时，**必须**遵循此结构化格式。**严禁**输出纯文本或无格式列表。

```markdown
# 项目特定规则: {Project Name}

## 🏗 架构与模式
- **Pattern Name**: {描述}
- **Pattern Name**: {描述}

## 🎨 编码规范
- **Standard**: {详细描述}
- **Standard**: {详细描述}

## 🚫 避免 / 阻断 (Avoid / Blockers)
- **Constraint**: {需避免的内容及原因}

## 💡 技巧与最佳实践
- **Tip**: {有帮助的背景信息}
```

**反模式警告**: 避免使用 `\n` 字面量字符串。请使用实际的换行符和 Markdown 列表项。
