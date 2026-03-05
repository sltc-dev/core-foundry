# File Scope Rules

## Principles

- Inspect the real repository tree before listing files.
- Use repo-relative paths exactly as they exist.
- Separate `confirmed` from `suspected`; never present guesses as facts.
- Explain why each file changes, not just which path changed.
- Reuse existing naming; do not invent path aliases.
- If scope expands during implementation, update the change spec before more code changes.

## Scan Order

1. Existing docs: check `docs/changes/` and nearby task/design docs.
2. Entry point: identify route, page, command, job, or bootstrap module.
3. Direct layer: inspect directly affected view/module.
4. Dependencies: inspect child components/hooks/stores/services used by that layer.
5. Config/schema: inspect flags, constants, validation schema, or build config only if touched.
6. Verification: inspect tests that should move with the change.
7. External boundary: inspect backend/infra only when the change truly crosses boundary.

## Output Format

| Status | Layer | File | Planned Change |
| --- | --- | --- | --- |
| confirmed | view | `src/views/login/index.vue` | Adjust user-facing error behavior |
| confirmed | service | `src/api/auth.ts` | Align request/response handling |
| suspected | test | `src/__tests__/views/login.spec.ts` | Add or update unit coverage |

## Escalation Cues

- Touching shared components, shared state, router, or cross-page behavior usually means `risky`.
- Touching contracts, schemas, persisted data, or backend boundaries usually means `risky`.
- Test/docs files do not raise level by themselves.

## Validation Scope

- Validation plan should include only:
  - `eslint`
  - `ts/typecheck`
  - `unit test`
