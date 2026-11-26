---
name: fastapi-feature-implementation
description: Implements ecommerce-backend FastAPI features in the existing endpoint-schema-service-model architecture with async SQLAlchemy, Pydantic v2, auth, transactions and tests.
---
# FastAPI Feature Implementation

## Decision branches
- Existing endpoint/schema/service/model exists: extend it, do not create duplicate module.
- No equivalent exists: inspect naming/router conventions before proposing new file.
- DB schema changes: coordinate Database Engineer and use database-migration skill.
- Payment behavior changes: use payment-lifecycle skill.
- Auth/ownership changes: include security review.

## Procedure
1. Inspect dependencies and nearest equivalent feature.
2. Confirm acceptance criteria and API contract.
3. Add/update request and response schemas with validation.
4. Update model only if needed; verify Base metadata registration.
5. Implement business logic in service.
6. Keep endpoint thin; register router using existing aggregator.
7. Enforce current auth/role/ownership dependencies.
8. Preserve transaction and error conventions.
9. Add success, validation, auth, ownership, not-found, conflict and failure tests.
10. Run focused and relevant regression tests.
11. Handoff changed files, decisions, migration impact and exact test evidence.

Never trust client totals/prices/stock/status. Never impose new architecture. Never claim unrun tests passed. Always use meaningful, complete words for every variable, property, and parameter name (never `_`, single-letter names, or incomplete/abbreviated words).
