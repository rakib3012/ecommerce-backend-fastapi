---
name: release-readiness
description: Performs ecommerce-backend pre-release verification for code changes, tests, secrets, Docker Compose, sandbox payment mode, health checks and rollback without deploying, migrating, or running git/gh.
---
# Release Readiness

- **Prohibited / Gated:** Never run `alembic` commands or modify `alembic/versions/`. Only run `git`/`gh` commit or push commands when explicitly requested by the user.
- Inspect modified application files (`models/`, `schemas/`, `services/`, `api/v1/endpoints/`) directly.
- Run actual configured tests, lint, type and build checks.
- Confirm env variable names documented and no secrets in source/image/logs.
- Verify PostgreSQL/Redis health, readiness and persistent volumes.
- Verify SSLCommerz remains sandbox unless approved.
- Check rollback and backward compatibility.
- Do not deploy or run production operations without approval.
- Return PASS/FAIL/BLOCKED/NOT RUN with evidence.
