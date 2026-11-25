# ecommerce-backend Antigravity Engineering System

## Installation
Merge root `AGENTS.md` and `.agents/` into the existing backend repository root. Do not blindly overwrite an existing AGENTS.md or customization files; merge and resolve duplicates. Open repository root in Antigravity IDE and verify Customizations/Agents, Rules and Skills.

## Agents
- `ecommerce-backend-orchestrator` — primary coordinator.
- `ecommerce-backend-product-analyst` — requirements.
- `ecommerce-backend-codebase-architect` — read-only reconnaissance.
- `ecommerce-backend-fastapi-engineer` — backend.
- `ecommerce-backend-database-engineer` — PostgreSQL/Alembic.
- `ecommerce-backend-frontend-engineer` — Next.js when source exists.
- `ecommerce-backend-payment-engineer` — SSLCommerz/COD.
- `ecommerce-backend-qa-engineer` — test design/execution.
- `ecommerce-backend-code-reviewer` — independent read-only review.
- `ecommerce-backend-security-reviewer` — read-only security.
- `ecommerce-backend-devops-engineer` — infrastructure/release.

## Skills
`feature-orchestration`, `codebase-reconnaissance`, `fastapi-feature-implementation`, `database-migration`, `inventory-concurrency`, `payment-lifecycle`, `qa-test-cycle`, `independent-code-review`, `prd-traceability`, `release-readiness`.

## Usage
Start multi-layer work with `/feature-orchestration`. Start first audit with `/codebase-reconnaissance` and `/prd-traceability`. Use specialist skills for focused tasks.

## Safety
All custom agents use `commandExecutionPolicy: sandbox`. Approval required for destructive DB operations, production deploy/migrations, live payment, real customer messaging, secrets changes, breaking API changes and architecture replacement.

## Source limitation
This package is based on PRD v2.0 and screenshots of backend folder structure. Complete Python source, DB schema, Alembic history, test suite and frontend repository were not supplied for direct inspection. Agents must inspect them before coding.


# ecommerce-backend-fastapi
