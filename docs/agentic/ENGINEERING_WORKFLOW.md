# ecommerce-backend Agent Workflow

Task states: REQUESTED -> ANALYZING -> PLANNED -> IMPLEMENTING -> TESTING -> REVIEWING -> REMEDIATING -> VERIFIED -> DOCUMENTED -> DONE (or BLOCKED).

| Stage | Owner | Output |
|---|---|---|
| Requirements | Product Analyst | Acceptance criteria, edge cases, questions |
| Reconnaissance | Codebase Architect | Verified conventions, impact map |
| Plan | Orchestrator | File ownership, sequence, risks |
| Backend | FastAPI Engineer | Implementation and focused tests |
| Database | DB Engineer | Constraints/migration/transaction review |
| Frontend | Frontend Engineer | UI/API alignment |
| Payment | Payment Engineer | Verified state/idempotency design |
| QA | QA Engineer | Test matrix and execution evidence |
| Security | Security Reviewer | Security findings |
| Review | Code Reviewer | Independent diff verdict |
| Integration | Orchestrator | Remediation, docs, final report |

Parallelize only independent work. Never have agents edit the same file simultaneously. QA can draft tests during implementation but final execution occurs after code stabilizes. Reviewers inspect final diff. If subagents unavailable, run role-based sequential passes and disclose.
