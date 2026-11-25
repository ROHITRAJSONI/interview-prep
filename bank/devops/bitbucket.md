# Bitbucket

## Q: What branching strategy and PR controls have you set up in Bitbucket?
### Solution
**Strategy:** trunk-based development with short-lived feature branches (`feature/JIRA-123-desc`) merged into `main` behind feature flags, or GitFlow (`develop`, `release/*`, `hotfix/*`) where release trains are scheduled, which is common in banks.

**Controls** (Bitbucket branch permissions + merge checks):
- No direct pushes to `main`/`release/*`; PR only.
- Minimum approvals (e.g. 2), **default reviewers** by path, reset approvals on new commits.
- Required green build, no unresolved tasks, merge strategy fixed (squash or merge commit).
- **Jira smart commits / branch names** linking every change to a ticket for audit (SOX / change-management evidence).

## Q: How does a Bitbucket Pipelines CI build work?
### Solution
Pipelines are defined in `bitbucket-pipelines.yml` at the repo root. Each **step** runs in a fresh Docker container (an `image:`) and can define **caches** (`maven`, `gradle`), **artifacts** passed between steps, **services** (e.g. a Postgres container for integration tests), and `parallel` blocks. You can configure pipelines per branch, per PR or per tag, with **deployment environments** (test/staging/prod) and manual triggers/approvals for prod. Secrets go in **secured repository/deployment variables**, or use OIDC to assume an AWS role without long-lived keys. Many enterprises instead pair Bitbucket Server/Data Center with Jenkins via webhooks.
