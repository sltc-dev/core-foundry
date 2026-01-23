# General CR Checklists

These are common "Red Lines" and best practices that apply unless specifically overridden by project rules.

## 🔴 Hard Red Lines (Blockers)
1. **No `any`**: TypeScript files must not use `any` unless explicitly justified.
2. **Debug Leaks**: No `console.log`, `debugger`, or commented-out large blocks of code.
3. **Hardcoded Secrets**: No API keys, passwords, or sensitive env vars in code.
4. **Localization**: No Chinese/Japanese characters in source code (must use i18n/constants).
5. **Async Errors**: No `await` inside loops without proper handling; no unhandled promise rejections.

## 🟡 Clean Code Standards
1. **Naming**: Variables should be descriptive; avoid `data`, `item`, `list` without context.
2. **Function Length**: Functions exceeding 50 lines should be considered for refactoring.
3. **DRY**: Repeated logic (3+ times) must be extracted to `utils` or shared components.

## 🔵 Project Consistency
1. **Tooling**: Always prefer project-specific `Utils` or `Hooks` over standard library if they exist.
2. **Patterns**: Respect existing architectural patterns (e.g., if the project uses Pinia, don't use reactive objects for global state).
