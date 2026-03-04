# Blocking Question Checklist

## Rules

- Ask only when the answer changes scope, classification, file plan, or validation.
- Ask no more than 3 questions in one turn.
- Prefer one question that resolves multiple uncertainties.
- If a safe assumption is possible, record it in the spec instead of asking.
- If the user already provides a change spec path, read it first and do not repeat answered questions.

## Priority Order

1. What exact outcome defines success for this change?
2. Where does the change start: route, page, command, job, or module?
3. What must remain unchanged: compatibility, UI behavior, public API, or directory boundaries?
4. Does this touch sensitive flows, shared contracts, persisted data, or backend coordination?
5. What validation or review must happen before the work is considered complete?

## Bug / Fix

- Where can the issue be reproduced reliably?
- What is the current behavior and what is the expected behavior?
- Is there a known suspect file, recent change, or failing request?
- Is the impact limited to one client, environment, or role?

## Feature

- Who is the target user and what new action should they be able to complete?
- What is the primary path and what are the important failure states?
- Should the change reuse existing components, APIs, stores, or patterns?
- Does it require analytics, permissions, feature flags, or configuration?

## Refactor

- What problem is the refactor solving: complexity, duplication, performance, or reliability?
- Must UI and external behavior remain identical?
- Which modules must stay compatible and which can change together?
- Is file movement, abstraction extraction, or directory restructuring allowed?

## Chore

- Is this purely tooling, config, docs, or mechanical cleanup?
- Does it affect runtime behavior, build output, or deployment?
- Is there a preferred existing convention to follow?

## Project

- What is the smallest first release that counts as done?
- What is explicitly out of scope for the first version?
- Which platforms, environments, or consumers matter first?
- Are there fixed technology, design, compliance, or integration constraints?

## High-Risk Follow-Up

- Does this require migrations, staged rollout, or feature-flag control?
- Who provides human review and final acceptance?
