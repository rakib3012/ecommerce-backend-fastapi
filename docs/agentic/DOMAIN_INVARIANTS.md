# ecommerce-backend Domain Invariants

## Inventory
Stock is per ProductVariant. Checkout locks affected variants using SELECT FOR UPDATE in deterministic ID order, checks stock after lock, returns 409 if insufficient and prevents negative stock. Order/items/stock mutations share a transaction. PRD requires concurrency test with stock=1 and two simultaneous checkout requests.

## Payment/order
Lifecycle: PENDING_PAYMENT -> CONFIRMED -> PROCESSING -> SHIPPED -> DELIVERED; exceptions PAYMENT_FAILED/CANCELLED.
COD: CONFIRMED + UNPAID, atomic stock deduction.
SSLCommerz: Init -> hosted gateway -> verified IPN; unique tran_id/idempotency; redirect is not proof. Eligible failure/cancel restores stock exactly once.

## Abandoned checkout
Separate from order creation; no stock lock/decrement; upsert same session; cart snapshot is not trusted for final price/stock; token random, single-use, 7-day expiry; expired ->410; order linkage may match recent phone/email within 24 hours per PRD.

## Comparison and wishlist
Comparison accepts 2–4 products; 5 ->400; out-of-stock sizes excluded; batch query target <150ms.
Wishlist unique `(user_id, product_id)`; duplicate add safely handled; PRD expects 200.

## Thresholds
Storefront low-stock badge <=3. Admin low-stock alert <5. Do not merge.

## Open decisions
Online-payment inventory reservation timing; order/payment transition map in existing source; raw vs hashed recovery token; abandoned upsert identity; comparison_sessions persistence; address table/snapshot source.
