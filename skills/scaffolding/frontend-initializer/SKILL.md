---
name: frontend-initializer
description: 使用 shuluntc/shuluntc-frontend-templates 中的模版初始化新的前端项目。
---

# 前端项目初始化技能

此技能帮助用户通过标准模版快速启动新的前端项目。

## 使用方法

该技能利用 Python 脚本列出可用模版并初始化新项目。

### 1. 列出可用模版

要查看仓库中可用的模版（列出所有找到的模版）：

```bash
python3 .agent/skills/scaffolding/frontend-initializer/scripts/init_project.py list
```

### 2. 初始化项目

要从特定模版创建新项目：

```bash
python3 .agent/skills/scaffolding/frontend-initializer/scripts/init_project.py create <template_name> <project_name>
```

示例：
```bash
python3 .agent/skills/scaffolding/frontend-initializer/scripts/init_project.py create react/nextjs-tailwind my-new-app
```

这将执行以下操作：
1. 创建一个名为 `<project_name>` 的目录。
2. 将所选模版的内容复制到该目录中。
3. 更新 `package.json` 中的 `name` 字段以匹配 `<project_name>`。

## 工作流

当用户想要初始化项目时：

1.  **列出模版**：首先查看有哪些模版可用。
    ```bash
    python3 .agent/skills/scaffolding/frontend-initializer/scripts/init_project.py list
    ```

2.  **创建项目**：选择一个模版名称（例如 `react/nextjs-tailwind`），运行创建命令：
    ```bash
    python3 .agent/skills/scaffolding/frontend-initializer/scripts/init_project.py create react/nextjs-tailwind my-new-app
    ```

    脚本将自动下载模版并设置 `package.json` 中的项目名称。
