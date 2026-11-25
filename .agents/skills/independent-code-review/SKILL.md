---
name: independent-code-review
description: Independently reviews ecommerce-backend diffs for architecture compliance, correctness, security, DB integrity, performance, commerce invariants and test adequacy.
---
# Independent Code Review

1. Read project constitution and acceptance criteria.
2. Inspect full diff and surrounding code.
3. Trace changed endpoint/schema/service/model/test path.
4. Check authorization, ownership and untrusted inputs.
5. Check Decimal pricing, stock locks, rollback and state machine.
6. Check payment verification/idempotency and recovery token.
7. Check constraints, migration safety and query loading.
8. Check tests are meaningful, deterministic and actually executed.
9. Classify findings Critical/High/Medium/Low with file/line.
10. Return BLOCKED / CHANGES REQUIRED / APPROVED WITH NOTES.

Do not edit. Critical/High findings block completion.
