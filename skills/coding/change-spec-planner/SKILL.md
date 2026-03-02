---
name: change-spec-planner
description: 将杂乱的功能需求、issues、bug 描述或新项目想法整理成规范的变更施工图 Markdown，并在写代码前固化到项目内。Use when a request needs to be clarified before implementation, when a code task must create or update a change spec in docs/changes, or when the work must be classified as lite, standard, or major for review and scope control.
---

# Change Spec Planner

## 核心目标

- 先产出 `docs/changes/*.md` 变更文档，再允许后续 AI 修改代码。
- 将用户的自然语言需求压缩为可执行的施工图，明确范围、文件、风险和验收标准。
- 让每次需求、issue、bug、重构或新项目都留下统一格式的历史记录。

## 执行流程

1. 判断任务类型：`fix`、`feat`、`refactor`、`chore`、`project`。
2. 依据 `references/risk-matrix.md` 判定 `lite`、`standard`、`major`。
3. 只追问阻塞实现的 1-3 个问题。优先使用 `references/question-checklist.md` 中对应类别的问题；非阻塞信息改写为假设，不要无限追问。
4. 根据 `references/file-scope-rules.md` 输出改动文件清单，并区分 `confirmed` 与 `suspected`。
5. 使用脚本生成文档骨架：

```bash
python3 .opencode/skills/change-spec-planner/scripts/init_change_doc.py \
  --title "优化登录错误提示" \
  --type fix \
  --level lite \
  --issue "#123"
```

6. 将以下内容补充到文档中：
- 背景
- 目标
- 非目标
- Mermaid 流程图
- 改动点
- 涉及文件
- 技术方案 / 依赖
- 结构约束
- 影响范围评估
- 验收标准
- 风险 / 回滚
- 待确认问题 / 假设
7. 按等级决定是否允许继续：
- `major`：文档生成后停止，等待人工 review。
- `standard`：默认建议 review；若用户明确要求，可在标记风险后继续。
- `lite`：文档生成后可直接进入实现。

## 写作规则

- 优先写清楚边界，而不是写长文。
- 明确写出 `非目标`，防止 AI 擅自扩大范围。
- 流程图统一使用 Mermaid，避免截图式流程图。
- 涉及文件必须写变更原因，不要只列路径。
- 如果实现中途新增文件或扩大范围，先更新变更文档，再改代码。

## 实施后更新

- 将变更文档继续作为单一事实来源，不要丢弃。
- 在实现完成后补充：
- `Implementation Result`
- `Actual Changed Files`
- `Deviation From Plan`
- `Verification`
- 如果实现结果与原计划不一致，先写差异，再解释原因。

## 资源导航

- `assets/templates/lite.md`：小改动模板。
- `assets/templates/standard.md`：常规需求模板。
- `assets/templates/major.md`：大改动模板。
- `references/question-checklist.md`：追问清单，控制提问数量。
- `references/risk-matrix.md`：分级与 review 规则。
- `references/file-scope-rules.md`：文件范围识别规则。
- `scripts/init_change_doc.py`：按命名规范生成变更文档。
