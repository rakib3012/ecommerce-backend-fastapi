---
trigger: glob
description: Async FastAPI, Python, Pydantic v2 and SQLAlchemy 2 implementation standards.
globs: "**/*.py"
---
- Inspect Python and installed dependency versions before using APIs or adding packages.
- Follow the project's actual async/sync DB style; never block async request handlers with synchronous I/O.
- Reuse shared engine/session dependencies; never create an engine per request.
- Use installed Pydantic v2 conventions and explicit request/response schemas.
- Do not accept client-supplied role, price, stock, payment/order status or computed totals.
- Keep endpoints thin; put business logic in existing services.
- Preserve current response/error envelope; do not invent a new one.
- Use Decimal/SQL Numeric for money; never float.
- Use timezone-aware timestamps consistent with the project.
- Handle known DB errors narrowly; do not swallow broad exceptions.
- Never expose hashes, tokens, secrets or internal provider details in responses/logs.
