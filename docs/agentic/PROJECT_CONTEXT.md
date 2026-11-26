# ecommerce-backend Project Context — Source Grounded

## Stack in PRD v2.0
Frontend: Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui.
Client state/data: TanStack Query, Zustand.
Backend: FastAPI async, Pydantic v2, SQLAlchemy 2.0, Alembic.
DB/search: PostgreSQL, tsvector, tsquery, pg_trgm.
Cache/rate limit: Redis.
Payments: SSLCommerz Sandbox and COD.
Media: Cloudinary/AWS S3.

## Screenshot-evidenced backend structure
`api/v1/endpoints`, `api/v1/api.py`, `api/v1/deps.py`, `core/config.py`, `core/database.py`, `core/security.py`, `models`, `schemas`, `services`, `main.py`, `requirements.txt`, `AGENTS.md`.

Screenshot modules include auths, carts, cart_items, categories, comparison_sessions, incomplete_orders, order_items, orders, payment_transactions, product_attributes, product_images, slug, users, wishlists; models also show products and product_variants.

## PRD scope
Catalog/variants; JWT and CUSTOMER/ADMIN; guest cart/merge; concurrency-safe checkout; coupons and regional delivery; SSLCommerz/COD; order state machine; admin; abandoned recovery; 2–4 product comparison; wishlist; recently viewed; size guide; low-stock indicator; sticky CTA; image zoom; estimated delivery.

## Gaps
Screenshots do not establish actual model fields, dependency signatures, async session style, response envelope, test fixtures, migration state or frontend location. Verify actual code.
