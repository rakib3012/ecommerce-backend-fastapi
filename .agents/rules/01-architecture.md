---
trigger: always_on
description: Preserve ecommerce-backend's existing FastAPI endpoint-schema-service-model architecture and real repository conventions.
---
- Actual source code defines current conventions; PRD v2.0 defines intended product behavior.
- Preserve `api/v1/endpoints`, `api/v1/api.py`, `api/v1/deps.py`, `core`, `models`, `schemas`, `services` where confirmed in source.
- Trace one comparable feature end-to-end before coding.
- Endpoint = HTTP/dependency orchestration; schema = validation/serialization; service = business logic; model = persistence; core = infrastructure.
- Reuse actual imports, async session lifecycle, auth dependencies, error mapping and router registration.
- Do not introduce repositories, CQRS, DDD, Clean Architecture, new package roots or duplicate modules without explicit approval.
- Screenshots are partial evidence; inspect actual source. Keep diffs focused.
