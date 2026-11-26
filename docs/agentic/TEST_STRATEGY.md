# ecommerce-backend Test Strategy

Layers: unit; service; async API; PostgreSQL integration; concurrency/idempotency; frontend component/integration where configured; repeatable performance benchmark.

Mandatory PRD cases:
- Same abandoned session captured twice -> no duplicate.
- Recovery token >7 days ->410.
- Resume restores correct cart.
- Compare five IDs ->400.
- Out-of-stock sizes excluded.
- Duplicate wishlist safely handled (PRD expects 200).
- Stock 3 shows low-stock; stock 4 hides.
- Two concurrent checkouts with one unit -> no oversell.
- Duplicate SSLCommerz IPN -> no duplicate payment/order/stock effect.
- COD -> CONFIRMED + UNPAID.

Use disposable PostgreSQL for DB behavior. Mock external payment network but test verification outcomes. Do not claim row-lock correctness from SQLite/mocks alone. Isolate Redis. Avoid arbitrary sleeps. Report exact commands, exit codes, counts, skipped and blocked tests.
