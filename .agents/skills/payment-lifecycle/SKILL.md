---
name: payment-lifecycle
description: Implements or audits ecommerce-backend SSLCommerz sandbox and COD lifecycle, verified IPN callbacks, transaction idempotency and order-state consistency.
---
# Payment Lifecycle

1. Inspect current payment/order models, services, routes, settings and tests.
2. Verify current SSLCommerz requirements using official provider docs; do not invent callback fields.
3. Define payment/order state transition table.
4. Keep credentials in environment variables.
5. Treat browser redirect as navigation only, never proof of payment.
6. Verify transaction server-to-server; validate transaction ID, order, amount, currency and provider status.
7. Enforce unique transaction identity and idempotent callback processing.
8. Protect concurrent duplicate callbacks with DB constraints/transactions.
9. COD stays CONFIRMED + UNPAID.
10. Restore stock exactly once on eligible failure/cancel.
11. Test valid, invalid, duplicate, mismatch, replay, timeout and COD cases.
12. Use sandbox/mocks; no live payment without approval.

Document provider fields verified, transitions, idempotency, DB constraints, test evidence and unresolved risks.
