# Change Risk Matrix

## How To Classify

- Evaluate risk drivers first, then use scope signals as a tie-breaker.
- Use the highest level that clearly matches the work.
- When the level is unclear, round up one level and explain why.
- File count is only a hint. Repetitive low-risk edits do not become `major` just because there are many files.

## Major

Treat the change as `major` if any of these are true:

- It changes authentication, authorization, billing, payment, identity, security, or other sensitive flows.
- It changes API contracts, persisted data schemas, cache formats, local storage formats, or migration behavior.
- It requires frontend and backend or service coordination across boundaries.
- It changes deployment strategy, rollout sequencing, feature flags, or requires a rollback playbook.
- It restructures shared architecture or multiple primary user flows.
- It is still materially unclear, but the uncertainty already spans multiple modules.
- The user explicitly says the change is large or high-risk.

Review rule:

- Write the spec, then stop and wait for human review approval and explicit user confirmation.

## Standard

Treat the change as `standard` when it is bounded but not purely local:

- It touches multiple layers in one repo, such as view, component, state, API, config, or tests.
- It changes shared components, routing, shared state, or cross-page behavior without changing sensitive contracts.
- It adds or updates a dependency with local impact only.
- It needs meaningful tests, docs, telemetry, or migration notes.
- It has moderate uncertainty, but the affected surface is still bounded.

Review rule:

- Recommend review first.
- Stop after the spec is ready.
- Continue only if the user explicitly accepts the risk and asks to proceed.

## Lite

Treat the change as `lite` when all of these are true:

- The change is localized to one bounded feature area.
- It does not change shared contracts, persisted data, or sensitive flows.
- Rollback is straightforward.
- Verification is local and easy to describe.

Review rule:

- Write the spec, then stop and wait for explicit user confirmation before implementation.

## Scope Signals (Secondary)

- `1-2` tightly related files usually suggests `lite`.
- `3-6` related files usually suggests `standard`.
- `7+` files requires an explicit explanation of why the scope is still bounded.
- Shared modules, routers, schemas, and cross-flow behavior raise risk faster than raw file count.
- Test files and documentation usually inherit the level of the product change; they do not raise the level by themselves.

## Default Action

- `lite`: create or update the spec, then ask for approval to proceed.
- `standard`: create or update the spec, flag risk, and ask for approval to proceed.
- `major`: create or update the spec, request review, then ask for explicit approval to proceed.
