---
trigger: always_on
description: ecommerce-backend authentication, RBAC, ownership, payment and customer data security requirements.
---
- Enforce CUSTOMER/ADMIN authorization in backend, not only frontend.
- Verify ownership for every user-scoped cart, wishlist, order and address operation.
- Reuse current password/JWT/refresh-cookie implementation; inspect actual claims and cookie settings.
- Do not trust client price, stock, role, payment state or order state.
- Verify SSLCommerz callback/IPN server-side; never treat browser redirect as proof.
- Recovery tokens must be random, expiring and single-use.
- Use environment variables for secrets; never commit .env.
- Never log credentials, tokens, provider secrets or unnecessary customer PII.
- Preserve CORS allowlist, Redis rate limits and cookie security; do not weaken to pass tests.
