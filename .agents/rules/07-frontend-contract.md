---
trigger: glob
description: ecommerce-backend Next.js App Router, TypeScript, TanStack Query, Zustand and backend contract rules.
globs: "**/*.ts, **/*.tsx"
---
- Apply only if frontend source exists in workspace.
- Inspect package.json, versions, app tree, API client, UI library and stores before coding.
- Preserve App Router server/client boundaries.
- Use TanStack Query for server state and Zustand for client state according to existing usage.
- Match actual FastAPI schemas/OpenAPI; never invent endpoints or response fields.
- Keep pricing, coupons, inventory, payment and authorization authoritative on backend.
- Include loading/error/empty/success states, accessibility and responsive behavior.
- Do not add libraries without checking dependencies and approval.
