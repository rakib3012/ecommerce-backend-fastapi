---
name: qa-test-cycle
description: Creates and executes ecommerce-backend QA matrix covering pytest unit, async API, PostgreSQL integration, regression, inventory concurrency and payment idempotency.
---
# QA Test Cycle

1. Read acceptance criteria.
2. Inspect pytest config, fixtures, async client and DB setup.
3. Map each criterion to tests.
4. Cover happy path, invalid input, auth/RBAC, ownership, errors and edge cases.
5. Use real DB integration for constraints/transactions.
6. Add inventory concurrency and payment idempotency tests.
7. Run focused tests, then relevant regression suite.
8. Run configured lint/type/build checks if installed.
9. Record exact commands, exit codes, pass/fail/skipped/blocked counts.
10. After fixes, rerun affected tests.

PRD baseline: same-session abandoned upsert; expired recovery ->410; cart restore; compare 5 IDs ->400; exclude OOS sizes; duplicate wishlist safe (200 expected); stock 3/4 low-stock boundary; stock=1 concurrent checkout; duplicate IPN no duplicate effects; COD confirmed/unpaid.
