---
name: project-guide-doc
description: 项目开发指南文档生成器。自动分析项目结构、技术栈和常用命令，生成全面的 DEVELOPMENT_GUIDE.md 文档。适用于新成员入职、项目文档维护和团队知识管理。触发场景包括："创建项目文档"、"生成开发指南"、"写项目README"、"项目怎么开始"、"新人如何上手"等。
---

# Project Guide Document Generator

## 概述

此 skill 帮助自动生成和维护项目的 DEVELOPMENT_GUIDE.md 开发指南文档。它会：
- 🔍 自动扫描项目结构和技术栈
- 📝 生成标准化的开发文档模板
- 🚀 提取常用命令和工作流程
- 📚 为新成员提供完整的入职指南

## 使用场景

当用户提出以下需求时使用此 skill：
- "帮我创建项目文档"
- "生成开发指南"
- "写一个 DEVELOPMENT_GUIDE"
- "新人怎么快速上手这个项目？"
- "需要一个项目说明文档"
- "更新项目的 README 或开发文档"

## 工作流程

### 第一步：了解项目需求

首先询问用户项目的基本信息（如果从对话中无法推断）：
- 项目的根目录路径是什么？
- 项目的主要用途是什么？（如：SaaS 平台、移动应用、API 服务等）
- 是否有特殊的架构或约定需要说明？

### 第二步：运行生成脚本

使用项目根目录运行生成脚本：

```bash
python3 scripts/generate_guide.py --project-root <项目根目录> [--output <输出路径>]
```

**参数说明**：
- `--project-root`: 项目的根目录路径（必需）
- `--output`: 输出文件路径（可选，默认为 `docs/DEVELOPMENT_GUIDE.md`）
- `--project-name`: 项目名称（可选，默认从目录名推断）
- `--update`: 更新现有文档而不是覆盖（可选）

**示例**：
```bash
# 为当前项目生成开发指南
python3 scripts/generate_guide.py --project-root /Users/username/my-project

# 自定义输出路径
python3 scripts/generate_guide.py --project-root /Users/username/my-project --output docs/DEV_GUIDE.md

# 更新现有文档
python3 scripts/generate_guide.py --project-root /Users/username/my-project --update
```

### 第三步：审阅和定制

脚本会生成包含以下章节的文档：
1. **项目概述** - 项目简介和主要功能
2. **架构与项目结构** - 目录结构和关键文件说明
3. **技术栈** - 使用的语言、框架和工具
4. **开发环境设置** - 安装依赖和配置步骤
5. **常用命令** - 开发、测试、构建等命令
6. **编码规范** - 代码风格和最佳实践
7. **API 文档** - API 端点和使用说明（如适用）
8. **故障排除** - 常见问题和解决方案

生成后，建议：
- 审阅自动生成的内容
- 补充项目特定的细节
- 添加团队约定和业务逻辑说明

### 第四步：维护和更新

建议定期更新开发指南：
- 当添加新功能模块时
- 当技术栈发生变化时
- 当团队规范更新时

使用 `--update` 参数可以保留手动添加的内容。

## 脚本功能说明

`generate_guide.py` 脚本会自动检测：

### 技术栈识别
- **前端**：package.json (Node.js, React, Vue, Next.js 等)
- **后端**：requirements.txt (Python), go.mod (Go), package.json (Node.js)
- **移动端**：pubspec.yaml (Flutter), Podfile (iOS), build.gradle (Android)
- **数据库**：配置文件中的数据库连接信息

### 项目结构分析
- 扫描主要目录（src/, app/, pages/, components/ 等）
- 识别配置文件和重要文档
- 提取项目模式（单体应用、微服务、前后端分离等）

### 命令提取
- npm/yarn scripts (package.json)
- Python 脚本 (scripts/ 目录)
- Makefile 命令
- Docker 命令（如有 Dockerfile）

## 最佳实践

参考 [guide_writing_best_practices.md](references/guide_writing_best_practices.md) 了解：
- 如何编写清晰的开发文档
- 优秀入职指南的要素
- 文档结构的组织原则
- 保持文档更新的策略

## 模板定制

如需自定义文档模板，可编辑 `assets/DEVELOPMENT_GUIDE_TEMPLATE.md`。模板使用以下占位符：

- `{{PROJECT_NAME}}` - 项目名称
- `{{PROJECT_DESCRIPTION}}` - 项目描述
- `{{TECH_STACK}}` - 技术栈列表
- `{{DIRECTORY_STRUCTURE}}` - 目录结构树
- `{{SETUP_COMMANDS}}` - 安装和设置命令
- `{{DEV_COMMANDS}}` - 开发常用命令
- `{{BUILD_COMMANDS}}` - 构建和部署命令

## 注意事项

1. **首次生成**：脚本会创建 docs/ 目录（如不存在）
2. **更新模式**：使用 `--update` 时会尝试合并现有内容，但请先备份
3. **手动补充**：自动生成的内容是基础框架，需要补充业务逻辑和团队约定
4. **版本控制**：建议将生成的文档纳入版本控制

## 示例输出

生成的 DEVELOPMENT_GUIDE.md 将类似于：

```markdown
# My Project - Development Guide

## 📋 项目概述
[自动生成的项目描述]

## 🏗️ 架构与项目结构
[目录树和说明]

## 🛠️ 技术栈
- Frontend: React 18 + TypeScript
- Backend: Node.js + Express
- Database: PostgreSQL
...

## 🚀 开发环境设置
[安装步骤]

## 💻 常用命令
[npm scripts 和其他命令]
...
```

完整的模板请查看 `assets/DEVELOPMENT_GUIDE_TEMPLATE.md`。
