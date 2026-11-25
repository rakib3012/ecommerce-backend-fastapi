---
name: feature-orchestration
description: Orchestrates ecommerce-backend feature delivery from PRD interpretation and repository inspection through specialist implementation, QA, independent review, remediation, re-testing and documentation.
---
# Feature Orchestration

## When to use
New feature, multi-layer change, substantial bug fix or PRD implementation.

## Prohibited actions & primary scope
- **NO Database Migrations:** Never run `alembic` commands or create/edit/delete files in `alembic/versions/`.
- **Git/GitHub Only When Requested:** Do not run `git` or `gh` commands unless the user explicitly asks to commit and push.
- **Primary Scope:** Focus strictly on SQLAlchemy Models (`models/`), Pydantic Schemas (`schemas/`), business logic Services (`services/`), and FastAPI API Endpoints (`api/v1/endpoints/`).
- **Model-Save Reminder:** Whenever a SQLAlchemy model is created or modified, stop after saving the model file and explicitly remind the user to run the Alembic migration manually.

## Steps
1. Read root `AGENTS.md` and applicable `.agents/rules/*.md`; inspect relevant source files directly.
2. Ask Product Analyst to define acceptance criteria and edge cases.
3. Ask Codebase Architect to trace actual code and nearest comparable feature.
4. Compare criteria with verified implementation. Resolve conflicts before edits.
5. Plan files, ownership, API/model changes, risks, tests and approval gates.
6. Assign backend/frontend/DB/payment specialists to bounded scopes.
7. Avoid parallel edits to the same file.
8. QA writes tests mapped to criteria and runs them.
9. Independent Code Reviewer and Security Reviewer inspect final changes.
10. Fix Critical/High findings and rerun affected tests.
11. Update API/architecture/decision docs if requested.
12. Inspect changed files and report exact evidence (plus manual Alembic reminder if models changed).

## Stop conditions
After creating/modifying any SQLAlchemy model (stop and remind user to run Alembic manually), destructive DB operations, production deploy, live payment, real customer messaging, breaking API changes or architecture replacement.

## Completion
No feature is complete without tests and independent review. Report PASS/FAIL/BLOCKED/NOT RUN honestly.
