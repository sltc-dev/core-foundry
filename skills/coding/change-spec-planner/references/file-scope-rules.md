# File Scope Rules

## Principles

- Inspect the real repository tree before listing files.
- Use repo-relative paths exactly as they exist.
- Separate `confirmed` from `suspected`; never present guesses as facts.
- Explain why each file changes, not just which path changed.
- Reuse the repository's existing naming. Do not rename `views` to `pages`, `stores` to `store`, or `style` to `styles` unless those paths actually exist.
- If scope expands during implementation, update the change spec before changing more code.

## Scan Order

1. Existing docs: check `docs/changes/` and any nearby design or task docs.
2. Entry points: identify the main trigger, such as router, page, CLI command, background job, or app bootstrap.
3. View layer: trace the directly affected route, screen, page, or view.
4. UI modules: inspect child components, composables, hooks, and local utilities used by that view.
5. State layer: inspect stores, caches, form state, and data synchronization logic.
6. Service layer: inspect API clients, service modules, adapters, and shared helpers.
7. Config and schema: inspect env files, feature flags, constants, validation schemas, and build config.
8. Styling and assets: inspect theme files, CSS/Tailwind, translations, and static assets.
9. Verification: inspect tests, mocks, fixtures, and e2e coverage that should move with the change.
10. External boundaries: inspect backend, serverless, infra, or shared service code only when the change truly crosses that boundary.

## Common Directory Aliases

- View layer may live under `src/views`, `src/pages`, `app`, `routes`, or feature folders.
- State may live under `src/stores`, `src/store`, `store`, `pinia`, or feature-local modules.
- Service code may live under `src/api`, `src/services`, `src/shared`, `src/util`, or adapters.
- Styles may live under `src/style`, `src/styles`, `styles`, `assets`, or theme folders.
- External boundaries may live under `server`, `api`, `functions`, `cloud`, `workers`, or another package.

## Output Format

| Status | Layer | File | Planned Change |
| --- | --- | --- | --- |
| confirmed | view | `src/views/login/index.vue` | Adjust the user-facing error state |
| confirmed | service | `src/api/auth.ts` | Align request or response handling if needed |
| suspected | test | `src/__tests__/views/login.spec.ts` | Add or update coverage if behavior changes |

## Escalation Cues

- Touching shared components, shared state, or routers usually raises the change to at least `standard`.
- Touching contracts, schemas, persisted data, or backend boundaries may raise the change to `major`.
- Adding tests or docs follows the primary change and does not raise the level on its own.
