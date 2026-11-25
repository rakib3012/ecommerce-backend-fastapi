---
name: codebase-reconnaissance
description: Performs read-only architecture and implementation audit of the actual ecommerce-backend FastAPI repository before coding.
---
# Codebase Reconnaissance

1. Capture repository tree and git status.
2. Read Python version, requirements and project config.
3. Read main.py, router aggregator, deps, config, DB and security modules.
4. Inspect relevant endpoint/schema/service/model files.
5. Trace one comparable feature end-to-end.
6. Inspect ORM relationships, Base registration, Alembic history/current head.
7. Inspect pytest config, fixtures, async client and test DB.
8. Record env variable names only; never reveal values.
9. Compare source to PRD: IMPLEMENTED / PARTIAL / MISSING / UNKNOWN / CONFLICT.
10. Do not edit files or run destructive commands.

Deliver verified facts, assumptions, unknowns, conflicts, existing conventions, candidate files and safe implementation plan.
