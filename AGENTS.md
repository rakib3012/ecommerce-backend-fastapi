# ecommerce-backend — Repository Engineering Constitution

Read this file and applicable `.agents/rules/*.md` before every task. This repository is the source of truth for existing implementation patterns. The approved ecommerce-backend PRD v2.0 is the source of truth for intended product behavior. Never silently invent or reconcile missing details.

## 1. Product and stack
ecommerce-backend is a Bangladesh-focused, multi-category fashion/apparel e-commerce platform.

PRD v2.0 stack:
- Frontend: Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui.
- Client state/data: TanStack Query, Zustand.
- Backend: FastAPI async, Pydantic v2, SQLAlchemy 2.0, Alembic.
- Database/search: PostgreSQL, native FTS (`tsvector`, `tsquery`), `pg_trgm`.
- Cache/rate limiting/token blacklist: Redis.
- Payments: SSLCommerz Sandbox (bKash, Nagad, cards) and COD.
- Media: Cloudinary or AWS S3, according to actual configuration.
- Tests: Pytest and actual async/database fixtures available in the repository.
- Deployment documentation: Docker Compose.

PRD explicitly requires deterministic engineering. Do not introduce external AI/LLM dependencies or unrelated architecture.

## 2. Existing backend architecture evidenced by screenshots
The supplied VS Code screenshots show:
- `api/v1/endpoints/`: route modules
- `api/v1/api.py`: router aggregation
- `api/v1/deps.py`: dependencies
- `core/config.py`, `core/database.py`, `core/security.py`
- `models/`, `schemas/`, `services/`
- `main.py`, `requirements.txt`, existing `AGENTS.md`

Endpoint modules shown: `auths.py`, `cart_items.py`, `carts.py`, `categories.py`, `comparison_sessions.py`, `incomplete_orders.py`, `order_items.py`, `orders.py`, `payment_transactions.py`, `product_attributes.py`, `product_images.py`, `slug.py`, `users.py`, `wishlists.py`.

Model modules shown: cart items, carts, categories, comparison sessions, incomplete orders, order items, orders, payment transactions, product attributes, product images, product variants, products, users, wishlists.

This is partial screenshot evidence, not a full source audit. Inspect actual files, imports, class names, session style, relationships, router registration, tests and migration history before coding.

## 3. Architecture rules
Preserve the actual project layout and naming. Do not migrate to Clean Architecture, repository pattern, CQRS, DDD, a new `app/` package, or another folder structure merely because an agent prefers it. Do not rename pluralization/casing/suffixes for style.

Layer boundaries:
- Endpoints: HTTP routing, dependencies, status codes, request/response orchestration.
- Schemas: Pydantic validation and response serialization.
- Services: business rules, transaction orchestration, domain errors.
- Models: SQLAlchemy persistence mappings, constraints, relationships, indexes.
- Core: configuration, DB/session lifecycle, security primitives.
- Dependencies: DB session, current user, role checks.

Trace one comparable feature end-to-end before changing another. Reuse the nearest working pattern. Keep changes focused and avoid unrelated refactors.

Naming standard:
- Always use meaningful, complete words for every variable, property, attribute, and parameter name. Never use `_`, single-letter names, symbols, unmeaningful names, or incomplete/abbreviated words (e.g., use `admin_user: User = Depends(require_admin)` instead of `_: User = Depends(require_admin)`).

## 4. Commerce invariants
1. Server-authoritative pricing: calculate prices, discounts, coupons, delivery fees and totals from trusted DB records. Never trust client totals.
2. Stock is tracked at ProductVariant/SKU level.
3. Checkout locks affected variant rows using `SELECT ... FOR UPDATE`, in deterministic variant-ID order; check stock after lock; insufficient stock -> 409.
4. Order, order items, stock changes and payment state must be transactionally consistent.
5. COD is `CONFIRMED + UNPAID` and stock deduction is atomic (PRD).
6. SSLCommerz redirect is not proof of payment; verify provider-side transaction/IPN.
7. Payment callbacks are idempotent; protect unique `tran_id` or equivalent.
8. Eligible cancellation/payment failure restores stock exactly once.
9. Enforce order lifecycle: `PENDING_PAYMENT -> CONFIRMED -> PROCESSING -> SHIPPED -> DELIVERED`; exception states `PAYMENT_FAILED` and `CANCELLED`.
10. CUSTOMER resources (cart, wishlist, orders, addresses) must be scoped to authenticated owner. ADMIN routes require server-side role checks.
11. Wishlist has `UNIQUE(user_id, product_id)`; duplicate add must be handled normally, not 500.
12. Abandoned checkout capture upserts the same session; it does not create a pending order or lock inventory.
13. Recovery token is cryptographically random, single-use, expires after 7 days; expired token -> 410 per PRD.
14. Comparison accepts 2–4 product IDs; 5 IDs -> 400. Out-of-stock sizes are not available sizes.
15. Storefront low-stock badge threshold is `stock <= 3`; admin low-stock alert is `stock < 5`. These are different rules.
16. Abandoned checkout cart snapshot is not authoritative for price/stock at final checkout.
17. Do not log passwords, access/refresh tokens, recovery tokens, payment secrets or unnecessary customer PII.

## 5. PRD feature contracts
- Product parent -> ProductVariant size/color SKU.
- Color selection filters sizes; variant image changes; out-of-stock variants disabled.
- Search/filter: category, price, size, color, in-stock, sort; PostgreSQL FTS and URL-synced frontend filters.
- Auth: short-lived access token + HTTP-only refresh cookie, rotation and Redis blacklist; roles CUSTOMER/ADMIN.
- Guest-to-user cart merge after login.
- Coupons: percentage/fixed; delivery fee Inside/Outside Dhaka.
- Abandoned capture: debounced frontend request, max one per 3 seconds/session; no pending order and no inventory lock.
- Recovery: single-use 7-day link; admin queue paginated, date-filterable and searchable by phone/email; link actual order to matching recent record per PRD 24-hour rule.
- Comparison: image/title/current+original price/fabric/sizes/colors/average rating/count; batched query; target <150ms.
- Wishlist: DB for logged-in user, localStorage guest, merge at login.
- Recently viewed: last 10 products.
- Size guide: Men/Women/Kids.
- Sticky mobile add-to-cart, image zoom, estimated delivery.
- Delivery estimate: Inside Dhaka +2 business days; outside +4 business days (clarify holiday calendar if needed).
- Admin metrics: revenue, order volume, pending shipments, low-stock alerts `<5`; inventory/order fulfillment/recovery queue.

## 6. Known conflicts and unknowns
- Screenshots show `incomplete_orders.py` / `Incomplete_orders_model.py`; PRD calls the feature/table `abandoned_checkouts`. Inspect semantics and migrations. Do not create a duplicate table or rename without approval.
- PRD NFR says cryptographically random 32-byte recovery token; task breakdown mentions UUID4 + `secrets.token_urlsafe`. Inspect current implementation and propose a secure design; do not silently break an existing token contract.
- PRD does not fully define online payment inventory reservation timing. Inspect code and ask before deciding.
- `comparison_sessions` is optional; PRD says localStorage can be initial implementation.
- Screenshots do not prove frontend source is in this workspace, actual model fields, error envelope, auth dependency signatures, test framework or Alembic state.

## 7. Mandatory agentic lifecycle
For non-trivial work:
1. Product Analyst: requirement, acceptance criteria, edge cases.
2. Codebase Architect: read-only source tracing and conventions.
3. Orchestrator: plan, file ownership, dependencies, risks and approval gates.
4. Backend/DB/Frontend/Payment specialist: scoped implementation.
5. QA Engineer: tests mapped to acceptance criteria and execution.
6. Independent Code Reviewer: final diff review.
7. Security Reviewer: review auth/payment/PII-sensitive changes.
8. Remediation and re-test.
9. Documentation and final evidence report.

Do not let multiple agents edit the same file concurrently. Parallelize only independent work or read-only analysis. If subagents are unavailable, perform role-separated sequential passes and disclose it; never pretend agents ran.

## 8. Safety / approval gates & prohibited actions
Strictly prohibited (never run or perform, even if seemingly helpful):
- **NO Database Migrations:** Never run any Alembic commands (`alembic revision`, `alembic upgrade`, `alembic downgrade`, etc.) and never create, modify, or delete files inside `alembic/versions/`. The human developer handles all database migrations manually.

Conditional / explicit-request-only actions:
- **Git & GitHub Operations:** Do NOT run `git` or `gh` commands (`git init`, `git add`, `git commit`, `git push`, etc.) on your own. Only run `git` / `gh` commit and push operations when the user explicitly asks you to commit and push. Never force-push or discard user work without explicit approval.

Primary scope of work:
- Focus strictly on application code: SQLAlchemy Models (`models/`), Pydantic Schemas (`schemas/`), business logic Services (`services/`), and FastAPI API Endpoints (`api/v1/endpoints/`).
- Whenever creating or modifying a SQLAlchemy model, stop after saving the model file and explicitly remind the user to run the Alembic migration manually.

Approval required before: DROP/TRUNCATE/reset/destructive operations; production/shared DB operations; production deploy; live payment mode; real customer SMS/WhatsApp/email; secrets rotation; breaking API changes; architecture replacement; major dependency changes.

Safe local tests, source inspection, and focused edits for an approved task may proceed.

## 9. Verification and reporting
Discover actual test commands, fixtures and dependency versions. Never assume pytest-asyncio, Ruff, mypy or coverage tools are installed. Add regression tests for bugs. Use real disposable PostgreSQL for constraints/transactions/concurrency; mocks alone do not prove DB behavior. Report PASS/FAIL/BLOCKED/NOT RUN with exact commands. Skipped/unrun tests are not passed.

Final response must state: acceptance criteria, files changed by layer, API changes, DB/migration impact, exact test commands/results, reviewer findings, remaining risks and approvals. Never claim “production-ready”, “fully tested” or “secure” without evidence.
