# AWS AppConfig / AWS Config

## Q: What's the difference between AWS AppConfig and AWS Config?
### Solution
They're often confused:
- **AWS AppConfig** (part of Systems Manager): *application* configuration and **feature flags**, deployed with controlled **rollout strategies** (linear/exponential over N minutes, bake time), JSON-schema/Lambda **validators**, and **automatic rollback** if a CloudWatch alarm fires. Apps fetch it via the AppConfig Agent (sidecar/Lambda extension) and cache it locally.
- **AWS Config**: *infrastructure* compliance. It records resource configuration history and evaluates **Config Rules** (e.g. "S3 buckets must not be public", "EBS must be encrypted"), with conformance packs and auto-remediation. That's a governance/audit tool.

## Q: How would you roll out a risky feature flag safely with AppConfig?
### Solution
1. Store the flag in an AppConfig feature-flag profile, with a validator so a typo can't ship.
2. Deploy with a gradual strategy (e.g. linear 20% every 2 minutes, then a 10-minute bake).
3. Attach CloudWatch alarms (error rate, p99) to the environment. If one breaches during the rollout or bake, AppConfig **automatically rolls back**.
4. The app reads through the AppConfig Agent with a short poll interval and a local cache, so an AppConfig outage never breaks requests; keep the last known good value.

Unlike Parameter Store, you get safe progressive delivery for configuration, not just storage.
