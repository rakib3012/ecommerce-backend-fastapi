# ecommerce-backend Antigravity Prompts

## First-run read-only audit
Read AGENTS.md, all rules and docs/agentic. Inspect repository tree, git status, dependencies, endpoints, schemas, services, models, DB setup, Alembic history and tests. Do not edit source or DB. Produce verified architecture, dependency inventory, PRD traceability, security gaps, test setup and prioritized roadmap. Separate facts/assumptions/unknowns/conflicts. Investigate incomplete_orders vs abandoned_checkouts. Wait for approval.

## Feature implementation
Use `/feature-orchestration`. Feature: [describe]. Read PRD, inspect existing pattern, define acceptance criteria, assign file ownership, delegate specialists, implement, write/run tests, request independent code/security review, fix findings, rerun tests and update docs. No destructive changes or architecture changes without approval. Report exact evidence.

## Bug fix
Bug: [describe]. Reproduce first. Trace route -> schema -> service -> model -> DB. Add regression test that fails before fix. Make smallest change following conventions. Run focused/regression tests. Independent reviewer inspects final diff. No unrelated refactor.

## Database change
Change: [describe]. Inspect model, metadata, Alembic history and data. Propose constraints/indexes/FK/backfill/downgrade. Generate migration but do not apply to valuable/shared/production DB without approval. Test disposable PostgreSQL.

## Release check
Use `/release-readiness`. Do not deploy. Inspect diff, tests, migrations, secrets, env docs, Docker health checks, sandbox payment and rollback. Return PASS/FAIL/BLOCKED/NOT RUN with evidence.
