---
trigger: always_on
description: Test-driven implementation, regression coverage, independent review and evidence-based completion.
---
- Inspect actual test config, fixtures, async client and DB setup before writing tests.
- Every behavior change needs tests; every bug fix needs a regression test.
- Cover success, validation, auth/RBAC, ownership, conflict, not-found and failure paths.
- DB constraints/transactions require DB integration tests; mocks alone are insufficient.
- Inventory needs concurrency test; payment callbacks need idempotency tests.
- Run focused tests then relevant regression suite and configured checks.
- Report exact commands and PASS/FAIL/BLOCKED/NOT RUN; skipped/unrun is not passed.
- Independent reviewer inspects final diff. Critical/High findings block completion.
