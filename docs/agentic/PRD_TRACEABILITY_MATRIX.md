# PRD v2.0 Traceability Matrix

This matrix records requirements, not current implementation status.

| PRD | Requirement | Verification evidence |
|---|---|---|
| p1–2 | Product scope, stack, deterministic/no external AI | requirements/package/config |
| p2 | Product parent + size/color SKU | ORM relations/API tests |
| p2 | Low stock <=3 | response + boundary tests |
| p2 | FTS and filters | PostgreSQL query/index/API |
| p2 | JWT rotation, HTTP-only refresh, Redis blacklist | auth/security tests |
| p2 | CUSTOMER/ADMIN | dependencies/role tests |
| p2 | Guest cart merge | endpoint/service tests |
| p2 | SELECT FOR UPDATE; insufficient stock 409 | service + PostgreSQL concurrency |
| p2 | Abandoned capture no order/no inventory lock | model/service/API tests |
| p2 | Coupons and regional delivery | pricing tests |
| p3 | SSLCommerz verified idempotent IPN | payment service + duplicate IPN test |
| p3 | COD CONFIRMED + UNPAID | order/payment test |
| p3 | Order state machine and stock restoration | transition and exactly-once tests |
| p3 | Admin low-stock alert stock <5 | admin query + threshold test |
| p3 | Comparison 2–4 products | API and frontend tests |
| p3 | Recently viewed last 10 | Zustand store tests |
| p3 | Wishlist DB/guest merge | uniqueness and merge tests |
| p3–4 | Size guide, sticky CTA, image zoom, delivery estimate | frontend component checks |
| p4 | abandoned_checkouts schema and FK | model/migration tests |
| p4 | wishlist unique pair | DB constraint/API duplicate test |
| p4 | product_attributes and optional comparison_sessions | migration/query tests |
| p5 | API surface | router/OpenAPI inventory |
| p5 | PLP TTFB <300ms | benchmark with environment |
| p5 | compare <150ms, max 4 IDs | API/performance test |
| p5 | Redis rate limits | auth/checkout/recovery tests |
| p5 | 32-byte random single-use 7-day token | token tests |
| p6–8 | roadmap and detailed tasks | implementation roadmap |
| p9 | abandoned, comparison, wishlist, low-stock tests | pytest suite |

Statuses: IMPLEMENTED (behavior + tests), PARTIAL, MISSING, UNKNOWN, CONFLICT. Never mark implemented from a filename alone.
