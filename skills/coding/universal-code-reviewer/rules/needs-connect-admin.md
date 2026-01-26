# 项目特定规则: needs-connect-admin

## 🏗 架构与模式
- **Framework**: Vue 3 + Vite
- **State Management**: Pinia (prefer for global state)
- **Data Fetching**: TanStack Vue Query (prefer for server state)
- **UI Library**: Element Plus
- **Styling**: Tailwind CSS v4

## 🎨 编码规范
- **Components**: PascalCase naming (e.g., `UserProfile.vue`)
- **Composables**: camelCase naming starting with `use` (e.g., `useUser.ts`)
- **Types**: Explicit types for props and emits. No `any`.
- **Imports**: Prefer absolute imports with `@/` alias for `src/` directory, though relative imports are acceptable for sibling files.

## 🚫 避免 / 阻断 (Avoid / Blockers)
- **State**: Do not use `vuex`. Use `pinia`.
- **Styling**: Do not write raw CSS unless necessary; use Tailwind utility classes.
- **Fetching**: Avoid raw `axios` calls in components; wrap in composables or services.
- **Console**: No `console.log` in production code.

## 💡 技巧与最佳实践
- **Element Plus**: Use auto-import if configured.
- **Typescript**: strict mode should be enabled.