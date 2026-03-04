---
name: change-spec-planner
description: Convert messy feature requests, bugs, refactors, chores, or project ideas into a scoped `docs/changes/*.md` implementation plan before code changes. Use when work needs clarification, when scope and risk must be classified as lite/standard/major, or when Codex should create or update a change spec as the single source of truth before and during implementation.
---

# Change Spec Planner

## Goal

- Create or update exactly one change spec before editing product code.
- Compress the request into an executable plan with explicit boundaries, file scope, risk, and validation.
- Keep the change spec current whenever scope, files, or rollout risk changes.
- Require explicit user confirmation after the spec is ready, before any implementation starts (all levels).

## Language Policy

- If the user explicitly requests a document language, follow that language.
- If the user does not specify language, write the change spec in Simplified Chinese by default.
- Do not switch to Japanese or other languages unless the user asks for it.
- Keep code, commands, and file paths in their original literal form.

## Workflow

1. Reuse an existing change spec when it already matches the request.
   - Search `docs/changes/` for the same issue ID, title, or feature area before creating a new file.
   - Update the existing spec instead of creating duplicates.
2. Inspect the real repository before guessing.
   - Read the relevant app structure, route tree, and existing docs first.
   - Use the repository's actual directory names; do not invent `pages`, `store`, or other paths that do not exist.
3. Classify the request.
   - Set the task type: `fix`, `feat`, `refactor`, `chore`, or `project`.
   - Set the level: `lite`, `standard`, or `major` using `references/risk-matrix.md`.
   - Treat file count as a secondary signal, not the primary risk rule.
4. Ask at most 3 blocking questions.
   - Use `references/question-checklist.md`.
   - Ask only when the answer changes scope, risk, or validation.
   - Convert non-blocking uncertainty into documented assumptions.
5. Build the file plan.
   - Use `references/file-scope-rules.md`.
   - Mark each path as `confirmed` or `suspected`.
   - Use repo-relative paths exactly as they exist and explain why each file changes.
6. Create or update the change spec.
   - Resolve `scripts/init_change_doc.py` relative to this skill directory.
   - Always pass `--repo-root <target-repo>` so the file is created in the correct repository.
   - Only pass `--output-dir` when the repository needs a non-default location.
   - Example:

```bash
python3 scripts/init_change_doc.py \
  --repo-root /path/to/repo \
  --title "Improve login error feedback" \
  --type fix \
  --level lite \
  --issue "#123"
```

7. Fill the spec using the matching template in `assets/templates/`.
   - Keep the document concrete, short, and actionable.
   - Write the validation plan before implementation starts.
   - Ensure the final spec language follows **Language Policy**.
8. Enforce the execution gate.
   - `lite`: stop after filling the spec and wait for explicit user confirmation to implement.
   - `standard`: recommend review first, then stop and wait for explicit user confirmation to implement.
   - `major`: stop after writing the spec and wait for human review approval plus explicit user confirmation.
   - Never start implementation just because the plan is complete.
9. Update the spec before code whenever scope changes.
   - If new files appear, risk increases, or the implementation deviates, revise the spec first.
   - After implementation, fill the closing sections instead of leaving the spec as draft-only paperwork.

## Required Content

- Background
- Goal
- Non-goals
- Flow or behavior summary
- File plan
- Implementation notes
- Validation plan
- Risk and rollback
- Open questions or assumptions
- Execution approval checkpoint
- Post-implementation result, file list, and verification

## Writing Rules

- Prefer explicit boundaries over long explanations.
- State non-goals to block scope creep.
- Keep the file plan and validation plan concrete enough for another engineer to execute.
- Use Mermaid for meaningful flow changes; if there is no meaningful flow change, say so plainly instead of inventing a diagram.
- Do not list speculative refactors that are not required for this request.
- If the task becomes larger than planned, raise the level and update the spec before continuing.
- Keep wording concise, direct, and operational; avoid mixed-language headings.
- After drafting or updating the spec, explicitly ask the user whether to proceed; do not assume approval.

## Bundled Resources

- `assets/templates/lite.md`: small, localized changes.
- `assets/templates/standard.md`: multi-file but bounded changes.
- `assets/templates/major.md`: high-risk or staged changes that need sign-off.
- `references/risk-matrix.md`: classify scope and review gate.
- `references/question-checklist.md`: ask only the minimum blocking questions.
- `references/file-scope-rules.md`: derive an accurate file plan from the actual repo.
- `scripts/init_change_doc.py`: create a correctly named spec file in the target repo.
