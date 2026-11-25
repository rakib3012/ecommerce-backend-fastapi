---
trigger: always_on
description: PostgreSQL integrity, SQLAlchemy relationships, transactions and strict prohibition on agent-run Alembic migrations.
---
- **NO Database Migrations:** Never run any Alembic commands (`alembic revision`, `alembic upgrade`, `alembic downgrade`, etc.) and never create, modify, or delete files inside `alembic/versions/`. The human developer handles all migrations manually.
- **Model-Save Reminder:** Whenever you create or modify a SQLAlchemy model (`models/`), stop after saving the model file and explicitly remind the user to run the Alembic migration manually.
- Inspect models, Base metadata imports, DB settings, constraints, and relationships first.
- Use DB constraints for invariants: FK, unique, check, not-null and indexes.
- Inventory checkout uses SELECT FOR UPDATE and deterministic variant-ID lock order.
- Order, order items, stock and payment mutations must be transactionally consistent.
- Never run DROP/TRUNCATE/reset or production/shared DB operations without explicit approval.
- PRD requires `abandoned_checkouts.recovered_order_id -> orders.id ON DELETE SET NULL`.
- Wishlist unique `(user_id, product_id)`; product_attributes index by product_id; stock non-negative.
- Resolve source/PRD schema differences before renaming or creating tables.
