---
name: inventory-concurrency
description: Implements and verifies ecommerce-backend SKU inventory safety, SELECT FOR UPDATE checkout, no-overselling constraints, rollback and exactly-once stock restoration.
---
# Inventory Concurrency

## Invariants
- Stock belongs to ProductVariant/SKU.
- Lock variants with SELECT FOR UPDATE in deterministic variant-ID order.
- Recheck stock after locks.
- Insufficient stock -> 409.
- Order/items/stock mutations share a transaction.
- DB CHECK prevents negative stock.
- COD = CONFIRMED + UNPAID with atomic deduction.
- Eligible cancel/payment-failure restores stock exactly once.

## Procedure
1. Trace existing checkout/order/variant model and transaction pattern.
2. Clarify whether online payment reserves stock; ask if ambiguous.
3. Implement ordered row locking in service.
4. Use Decimal for totals.
5. Define rollback for every failure point.
6. Protect duplicate cancellation/failure callback.
7. Add PostgreSQL integration test: two simultaneous checkouts, one remaining unit.
8. Add repeated cancellation/failure test proving one stock restoration.
9. Run against disposable PostgreSQL, not mocks/SQLite alone.
10. Report isolation and verification limitations.
