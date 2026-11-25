---
trigger: always_on
description: ecommerce-backend commerce invariants for pricing, SKU inventory, checkout, orders, payments, recovery and comparison.
---
- Server calculates prices, discounts, coupons, delivery fees and totals.
- Stock belongs to ProductVariant/SKU.
- Checkout locks variants in deterministic order, checks stock after lock, returns 409 when insufficient.
- COD = CONFIRMED + UNPAID with atomic stock deduction.
- SSLCommerz redirect is not payment proof; verify server-side IPN/provider transaction.
- Payment callbacks are idempotent; unique transaction identity; no duplicate stock/payment effects.
- Restore stock on eligible cancel/failure exactly once.
- Enforce order state transitions server-side.
- Abandoned capture upserts, creates no order and does not lock inventory.
- Recovery token random, single-use, 7 days; expired -> 410.
- Compare 2–4 IDs; 5 -> 400; exclude out-of-stock sizes.
- Wishlist duplicate must be safe; DB unique pair.
- Storefront low stock <=3; admin low-stock alert <5. Never conflate thresholds.
