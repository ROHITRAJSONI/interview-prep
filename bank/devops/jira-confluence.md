# Jira & Confluence

## Q: How do you break down and estimate a large feature in Jira?
### Solution
Epic → stories (vertical slices, each delivering user-visible value and independently deployable) → sub-tasks. Each story gets **acceptance criteria** (often Given/When/Then, which links straight to Cucumber tests) and a Definition of Done (tests, code review, docs, deployed to test).

Estimate in story points with the team (planning poker). Points measure relative complexity and risk, not hours. Use spikes for unknowns. Track sprint velocity, and use the burndown and cumulative flow charts to spot blockers. Link stories to commits/PRs (smart commits) for traceability, which matters for audit in regulated environments.

## Q: What do you put in Confluence for a service you own?
### Solution
- **Architecture / design doc** (context, C4 diagrams, key decisions recorded as ADRs with alternatives considered).
- **API docs** (link to the OpenAPI spec), event schemas, data contracts.
- **Runbook:** how to deploy and roll back, dashboards and alarms and what each one means, common incidents with step-by-step fixes, escalation contacts.
- **Onboarding:** local setup, environments, access requests.
- **Postmortems** (blameless) with action items tracked as Jira tickets.

Keep the docs close to the code where possible (README, docs-as-code) and link them from Confluence, so they don't rot.
