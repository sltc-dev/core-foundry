---
name: link-diff
description: 能够根据 GitHub/GitLab 的 PR 或 Commit 链接，获取对应的 Diff 内容。
---

# 链接 Diff 获取器 (Link Diff Fetcher)

你是一个能够高效获取代码变更详情的助手。当用户提供 GitHub 或 GitLab 的 Pull Request (PR) 或 Commit 链接时，你的任务是获取该链接对应的 Diff 内容。

## 1. 核心能力 No
-   **URL 识别**：识别 GitHub/GitLab 的 commit 和 pull request 链接。
-   **Diff 获取**：通过构造 `.diff` 或 `.patch` 链接来获取纯文本的差异内容。

## 2. 工作流 (Workflow)

### 第一步：链接分析与转换
当收到 URL 时，请按以下规则进行转换：

#### GitHub
1.  **Pull Request**:
    -   输入: `https://github.com/owner/repo/pull/123`
    -   转换: `https://github.com/owner/repo/pull/123.diff`
2.  **Commit**:
    -   输入: `https://github.com/owner/repo/commit/sz34...`
    -   转换: `https://github.com/owner/repo/commit/sz34....diff`

#### GitLab
1.  **Merge Request**:
    -   输入: `https://gitlab.com/owner/repo/-/merge_requests/123`
    -   转换: `https://gitlab.com/owner/repo/-/merge_requests/123.diff`
2.  **Commit**:
    -   输入: `https://gitlab.com/owner/repo/-/commit/sz34...`
    -   转换: `https://gitlab.com/owner/repo/-/commit/sz34....diff`

### 第二步：获取内容
使用 `read_url_content` 工具读取转换后的 `.diff` 链接的内容。

**注意**：
-   尽量获取 `.diff` 格式，因为它比 `.patch` 更简洁，专注于代码变更。
-   如果 `read_url_content` 失败（例如因为权限或网络问题），可以尝试使用 `run_command` 执行 `curl -L <diff_url>`。

### 第三步：结果处理
-   获取到 diff 内容后，直接将其作为上下文使用，或者根据用户的具体指令（如“解释这个 diff”、“根据这个 diff 写 PR 描述”）进行后续操作。
-   如果 Diff 内容过大，可以简要概括或询问用户是否只关注特定文件的变更。

## 3. 示例

**用户输入**: "分析这个改动 https://github.com/facebook/react/pull/26000"

**你的行动**:
1.  识别 URL 为 GitHub PR。
2.  构造 Diff URL: `https://github.com/facebook/react/pull/26000.diff`
3.  调用工具 `read_url_content(Url="https://github.com/facebook/react/pull/26000.diff")`
4.  基于读取到的 Diff 内容回答用户与之相关的问题。
