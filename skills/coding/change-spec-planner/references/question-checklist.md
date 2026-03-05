# Blocking Question Checklist (Small Team)

## Rules

- Ask only when the answer changes scope, level, file plan, or validation.
- Ask no more than 3 questions in one turn.
- Prefer one high-value question that resolves multiple uncertainties.
- If a safe assumption is possible, record it in the spec instead of asking.
- If a change spec path is already provided, read it first and avoid duplicate questions.

## Priority Order

1. What exact outcome defines success for this change?
2. Where does the change start (route/page/command/job/module)?
3. What must stay unchanged (compatibility, behavior, API, directory boundaries)?
4. Does it touch shared contracts, persisted data, sensitive flows, or cross-service boundaries?
5. Which commands should be used for the three required checks: `eslint`, `ts/typecheck`, `unit`?

## Type-Specific Prompts

### Bug / Fix

- How can the issue be reproduced reliably?
- What is current behavior vs expected behavior?
- Is there a suspect file, recent change, or failing request?

### Feature

- Who is the target user and what new action should be possible?
- What is the primary path and key failure state?
- Must it reuse existing components/APIs/state patterns?

### Refactor

- What concrete problem does this refactor solve?
- Must external behavior remain identical?
- Are file moves or directory restructuring allowed?

### Chore / Project

- Is this only tooling/docs/config, or does runtime behavior change?
- What is explicitly out of scope for this iteration?
- Are there fixed technology or integration constraints?

## Risky Follow-Up

- Who provides the required human review approval?
