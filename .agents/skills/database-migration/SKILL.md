---
name: database-migration
description: Designs PostgreSQL/SQLAlchemy model changes, constraints, indexes, and relationships for ecommerce-backend while enforcing manual human-only Alembic migrations.
---
# Database Model & Schema Design (No Agent-Run Migrations)

1. **Prohibited Actions:**
   - Never run any `alembic` commands (`alembic revision`, `alembic upgrade`, `alembic downgrade`, etc.).
   - Never create, modify, or delete any files inside `alembic/versions/`.
   - Never run `git` or `gh` commands unless the user explicitly asks to commit/push.
2. Inspect existing `models/`, `Base` imports, DB settings, constraints, and relationships first.
3. Confirm real schema/data requirements; do not infer from filenames alone.
4. Define nullability, defaults, FK delete behavior, uniqueness, check constraints, and indexes in the SQLAlchemy model.
5. Update the ORM model in `models/` (and `alembic/env.py` metadata import if needed).
6. **Stop after saving the model file** and explicitly remind the user to run the Alembic migration manually.

PRD checks: `abandoned_checkouts.recovered_order_id ON DELETE SET NULL`; wishlist unique `(user_id, product_id)`; `product_attributes` indexed by `product_id`; non-negative stock; unique payment `tran_id`. Resolve `incomplete_orders` vs `abandoned_checkouts` before rename/create.

Never run destructive or production DB operations without explicit approval.
