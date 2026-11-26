# ecommerce-backend Decisions and Conflicts

## DC-001: incomplete_orders vs abandoned_checkouts — OPEN
Screenshot shows incomplete_orders endpoint/model/schema/service. PRD uses abandoned_checkouts. Inspect table, data, migration and behavior. Propose compatibility/rename plan. Do not create duplicate table or rename without approval.

## DC-002: recovery token — OPEN
PRD NFR says cryptographically random 32-byte token; implementation task also mentions UUID4 + secrets.token_urlsafe. Inspect current design. Hash-at-rest may improve security but changes lookup. Propose and ask before breaking existing links.

## DC-003: online payment inventory timing — OPEN
PRD describes locking and COD deduction but does not fully specify online pending-payment reservation expiry. Inspect source and ask before deciding.

## DC-004: comparison_sessions — OPEN
Optional server-side table; localStorage may be initial approach. Confirm actual product need.

## DC-005: frontend workspace — OPEN
PRD names Next.js but supplied screenshots show backend. Inspect workspace folders before frontend delegation.
