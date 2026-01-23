# Feedback Templates

Use these templates when providing CR results.

## Classification Icons
- 🔴 **Blocker**: Critical issues, violations of "Red Line" rules, logic bugs, or security risks. Must be fixed.
- 🟡 **Suggestion**: Improvements for readability, maintainability, or performance. Non-blocking.
- 🔵 **Question**: Clarifications needed about business logic or intent.

## Review Result Template
```markdown
# Code Review Summary

## 🔴 Blocker ({blocker_count})
- **[File Name]**: {Description of the issue}
  - *Context*: Why this is a blocker in this project.
  - *Suggested Fix*: [Code snippet]

## 🟡 Suggestion ({suggestion_count})
- **[File Name]**: {Potential optimization}

## 🔵 Question ({question_count})
- {Questions for the user}

---
## 🏁 Conclusion
{Overall health score and summary}
```

## Evidence Pattern
When pointing out an inconsistency, use this format:
- "⚠️ Inconsistent with `{other_file.ts}`: This project typically uses `{pattern}`, but `{current_file.ts}` uses `{wrong_pattern}`."

## Project Rule Definition (IMPORTANT)
When defining or updating project rules (`rules/{project}.md`), you **MUST** follow this structured format. **NEVER** output raw text or unformatted lists.

```markdown
# Project Specific Rules: {Project Name}

## 🏗 Architecture & Patterns
- **Pattern Name**: {Description}
- **Pattern Name**: {Description}

## 🎨 Coding Standards
- **Standard**: {Detailed description}
- **Standard**: {Detailed description}

## 🚫 Avoid / Blockers
- **Constraint**: {What to avoid and why}

## 💡 Tips & Best Practices
- **Tip**: {Helpful context}
```

**Anti-Pattern Alert**: Avoid using `\n` literal strings. Use actual line breaks and Markdown list items.
