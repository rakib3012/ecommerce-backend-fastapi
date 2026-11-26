# Reusable Master Prompt — Generate a Project-Specific Agentic Engineering System

Copy this prompt into ChatGPT/your coding assistant for another project. Attach the PRD, architecture screenshots, repository tree, representative source files and reference agent instructions.

---

You are a Principal AI Engineering Architect and Antigravity Customization Specialist.

Design and generate a complete, project-specific Agentic Engineering System. Do not create generic boilerplate.

## Source analysis
1. Read the complete PRD and preserve its terminology, scope, constraints and priorities.
2. Inspect all screenshots and source files.
3. Separate verified facts, inferred facts, unknowns and conflicts.
4. Extract actual language/framework/library versions from project config.
5. Identify folder structure, naming, layer boundaries, DI, DB session lifecycle, auth/RBAC, error conventions, migrations, tests and deployment.
6. Trace at least one feature end-to-end (route -> schema -> service -> model -> tests).
7. Do not invent modules, fields, endpoints, env variables, commands or installed libraries.
8. Do not silently reconcile PRD/source contradictions.
9. If source code is missing, explicitly mark assumptions and make generated agents inspect repository before coding.

## Validate current IDE format
Research CURRENT official platform docs before generating:
- custom agent paths/frontmatter and supported values
- mainAgent/subagent behavior
- rules paths/triggers/frontmatter
- skills path/SKILL.md frontmatter
- discovery limitations/manifests
- command execution/permission policies
Do not use outdated or deprecated formats. Cite official docs.

## Required deliverables
A. Root AGENTS.md: project identity, stack, architecture, invariants, quality, security, testing, approval gates and DoD.
B. Custom agents with valid YAML frontmatter and detailed prompts: orchestrator, product analyst, read-only architect, actual backend specialist, DB specialist, frontend if present, payment/integration if needed, QA, independent reviewer, security reviewer, DevOps if relevant.
Each agent must include role/mission, stack context, technical directives, layer boundaries, domain invariants, security, step-by-step execution, tests, forbidden behavior, handoff and stop conditions. Follow the supplied reference agent's depth, not a short summary.
C. Focused persistent rules: architecture, language/framework, DB/migrations, domain invariants, security, tests/review, frontend contract, governance. Use valid triggers and respect discovery limitations.
D. Focused skills: feature orchestration, reconnaissance, backend feature, DB migration, domain-critical workflow, QA cycle, code review, PRD traceability, release readiness. Each has when-to-use, preconditions, steps, branches, stop conditions and deliverables.
E. Docs: project context, verified architecture, PRD traceability, domain invariants, delegation workflow, test strategy, decisions/conflicts, DoD, installation.
F. Reusable prompt for future setups.

## Agentic workflow
Requirement analysis -> source reconnaissance -> plan -> specialist implementation -> QA tests and execution -> independent code review -> security review as applicable -> remediation -> re-test -> docs -> final report.
Prevent concurrent edits to same file. If subagent delegation unavailable, use sequential role passes and disclose. Never pretend an agent ran.

## Quality bar
No shallow generic agents. No unrelated stack copied from sample. No invented facts. No unnecessary architecture/dependencies. Every rule actionable and testable. Include real domain invariants and edge cases. Require approval for destructive DB operations, production deployment, live payments, real customer messaging, secret changes, data deletion and breaking API/architecture changes. Report PASS/FAIL/BLOCKED/NOT RUN. Do not claim production-ready without evidence.

## Output
1. Source analysis and conflicts.
2. Full file tree.
3. Actual installable ZIP.
4. Installation and discovery verification.
5. First-run read-only audit prompt.
6. Feature development prompt.
7. Assumptions and repository checks still needed.

Do not stop at recommendations; create the files and ZIP.
