# AI Skill 贡献规范

> 为了让 `Core Foundry` 的能力能够被所有人轻松复用，我们需要遵循统一的技能定义规范。

## 📁 目录结构

每个技能（Skill）应位于 `skills/` 下的相关分类目录中，结构如下：

```text
skills/category-name/
└── skill-name/
    ├── SKILL.md          # 技能核心文档（必需）
    ├── scripts/          # (可选) 相关的自动化脚本
    └── examples/         # (可选) 使用示例或测试用例
```

## 📄 SKILL.md 编写模板

请遵循以下格式编写你的 `SKILL.md`：

```markdown
# 技能名称：[简短直观的名称]

> 描述：一句话说明这个技能解决了什么问题。

## 🎯 适用场景
- 场景 A
- 场景 B

## 🛠 使用方式
### 方式一：结构化 Prompt (适用于 ChatGPT/Claude/Kimi)
[在这里粘贴你的结构化提示词，推荐使用 Role-Task-Constraint 模式]

### 方式二：命令行/脚本 (如有)
```bash
python scripts/your_script.py --input data.csv
```

## ⚠️ 注意事项 & 技巧
- [提示技巧 1]
- [限制说明 1]

## ✍️ 贡献者
- @YourName (Department)
```

## ✅ 准入标准
1. **可复用性**：该技能是否具有普适性，而不只是解决一个极度极特殊的案例？
2. **结构化**：Prompt 是否经过优化（Role, Task, Constraints, Output Format）？
3. **验证过**：你是否已经在实际 AI 模型中测试过并能稳定输出？

---
[README.md](../../README.md) | [返回首页](../../README.md)
