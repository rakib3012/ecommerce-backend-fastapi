---
trigger: always_on
description: ecommerce-backend agent delegation, ownership, prohibited actions, primary scope and truthful reporting.
---
- **Strictly Prohibited:**
  - **NO Database Migrations:** Never run any `alembic` commands (`alembic revision`, `alembic upgrade`, `alembic downgrade`, etc.) and never create, modify, or delete files inside `alembic/versions/`.
- **Explicit-Request-Only Git/GitHub:** Do NOT run `git` or `gh` commands unprompted; only run `git` branch, commit, and push commands when the user explicitly requests you to commit and push.
- **Branch & Commit Standard (when committing/pushing by user request):**
  - **Branch Naming:** Use vertical-slice branches: `feat/<scope>`, `fix/<scope>`, `refactor/<scope>`, `test/<scope>`, `docs/<scope>`, or `chore/<scope>`.
  - **Conventional Commits:** Separate layers cleanly via commits on the feature branch (`feat(models): ...`, `feat(schemas): ...`, `feat(services): ...`, `feat(api): ...`, `feat(core): ...`, `test(...): ...`, `chore(...): ...`).
- **Primary Scope:** Focus strictly on SQLAlchemy Models (`models/`), Pydantic Schemas (`schemas/`), business logic Services (`services/`), and FastAPI API Endpoints (`api/v1/endpoints/`).
- **Model-Save Reminder:** Whenever creating or modifying a SQLAlchemy model, stop after saving the model file and explicitly remind the user to run the Alembic migration manually.
- Orchestrator owns acceptance criteria, plan, assignments, integration and final report.
- Specialists work within assigned scope and report changed files, tests, assumptions and blockers.
- QA and reviewer must be separate from implementation; do not self-certify.
- Avoid concurrent edits to the same files.
- If subagents unavailable, do sequential role-based passes and disclose.
- Ask before destructive DB operations, production deployment, live payments/messages, breaking API changes or architecture replacement.
- Never fabricate agent output, test results or source facts.
