# Change Risk Matrix (Small Team)

## How To Classify

- Evaluate risk drivers first, then use file count only as a tie-breaker.
- Use the highest level that clearly matches the work.
- When uncertain, classify as `risky` and explain why.

## Lite

Treat as `lite` when all are true:

- Change is localized to one bounded feature area.
- No shared contract, persisted data, schema, or sensitive flow changes.
- Rollback is straightforward.
- Verification can be completed with local `eslint`, `ts/typecheck`, and `unit` checks.

Gate:

- Write/update spec, then wait for explicit user confirmation.

## Risky

Treat as `risky` when any is true:

- Touches shared components, shared state, router, or cross-page behavior.
- Touches API contract, persisted data, schema, cache/storage format, or migration behavior.
- Crosses frontend/backend or service boundaries.
- Involves auth, permission, billing, identity, security, or other sensitive flows.
- Uncertainty spans multiple modules and could change scope during implementation.

Gate:

- Write/update spec.
- Require at least one human review approval.
- Continue only after explicit user confirmation.

## Scope Signals (Secondary)

- `1-3` tightly related files usually suggests `lite`.
- `4+` related files should be justified as `lite`; otherwise use `risky`.
- Shared modules/contracts raise risk faster than raw file count.
- Test/docs files inherit the level of the primary product change.

## Default Action

- `lite`: create/update spec, ask for explicit approval to proceed.
- `risky`: create/update spec, request review, then ask for explicit approval to proceed.
