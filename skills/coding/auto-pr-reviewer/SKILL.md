---
name: auto-pr-reviewer
description: 全自动 PR 审查助手。自动获取 GitHub PR Diff 并调用 Universal Code Reviewer 进行审查。
trigger_keywords: ["review pr", "pr review", "审查 pr", "review #", "cr #"]
execution_mode: strict
---

# Auto PR Reviewer

你是一个自动化的 PR 审查助手。你的工作是获取指定 PR 的变更（Diff），并严格遵循 Universal Code Reviewer 的标准进行审查。

## 核心工作流 (Core Workflow)

### Step 1. 启动审查任务

AI 必须执行 `skills/coding/auto-pr-reviewer/scripts/pr_worker.py` 脚本来编排整个流程。

命令格式：
```bash
python3 skills/coding/auto-pr-reviewer/scripts/pr_worker.py <pr_id_or_url>
```
*   `<pr_id_or_url>`: 用户提供的 PR 编号 (e.g., 123) 或完整的 PR URL。

**脚本将自动执行以下操作：**
1.  **Fetching Diff**: 使用 `gh_helper` 获取 PR 的 Diff 内容并保存通过临时文件。
2.  **Context Loading**: 自动调用 `skills/coding/universal-code-reviewer/scripts/rule_manager.py` 加载项目规则。
3.  **Instruction Generation**: 输出后续操作的明确指令。

### Step 2. 执行指令

脚本执行成功后，会输出类似以下的指令区块：

```text
🤖 [INSTRUCTIONS FOR AI AGENT]
1. Read the diff file: view_file /tmp/pr_{id}.diff
2. Review the code strictly following the [STATUS: READY] rules above.
3. You MUST declare '[CR Skill 激活]' at the start of your response.
```

**AI 必须严格照做：**
1.  使用 `view_file` 读取指定的 Diff 文件路径。
2.  **仔细阅读**脚本输出中的 `PHASE 1` / `PHASE 2` / `PHASE 3` 规则内容。

### Step 3. 执行审查 (Execution)

读取 Diff 后，**必须严格遵循 `skills/coding/universal-code-reviewer/SKILL.md` 中定义的所有规则和输出格式**进行审查。

**即便你是通过 `auto-pr-reviewer` 被唤起的，你也必须扮演 `Universal Code Reviewer` 的角色。**

你必须确认：
1.  **规则加载状态**：参考脚本输出中的 `[STATUS:READY]` 部分。
2.  **项目类型与规则**：参考脚本输出的 `PHASE 1` / `PHASE 2` / `PHASE 3`。

### Step 4. 输出报告

使用 Universal Code Reviewer 规定的输出模板生成最终报告。

**必须包含**：
- `## CR 执行检查` (确认已加载规则)
- `## 审查结果` (Blockers / Suggestions / Good Practices)
- `### 📊 总结`

---

## 异常处理

*   如果脚本提示 `Authentication failed`：请提示用户检查 `gh` CLI 登录状态。
*   如果脚本提示 `PR not found`：请检查 PR 编号是否正确。
*   如果 `universal-code-reviewer` 规则加载失败：请降级使用通用代码审查标准，并明确告知用户。
