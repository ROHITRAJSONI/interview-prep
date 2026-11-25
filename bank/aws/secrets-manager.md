# AWS Secrets Manager

## Q: Secrets Manager vs SSM Parameter Store: when do you use which?
### Solution
**Secrets Manager:** built-in **automatic rotation** (Lambda-based, native for RDS/Aurora/Redshift/DocumentDB), cross-region replication, and secrets up to 64 KB. It's priced per secret per month plus API calls.
**Parameter Store:** hierarchical config (`/app/prod/db/url`), `SecureString` with KMS, a **free** standard tier, versioning. No native rotation.

Rule of thumb: credentials that must rotate (DB passwords, API keys) go in Secrets Manager; everything else (config, feature flags, non-rotating secrets) goes in Parameter Store.

## Q: How do you rotate a database password without downtime?
### Solution
Use the **alternating-users** rotation strategy (two DB users, rotating the inactive one) or single-user rotation with the four steps `createSecret → setSecret → testSecret → finishSecret`. Secrets Manager moves the `AWSCURRENT`/`AWSPENDING` staging labels.

On the application side: don't cache credentials forever. Use the **AWS Secrets Manager JDBC driver wrapper** or a caching client with a short TTL, and on an auth failure refresh the secret and retry. Ensure the connection pool (Hikari) can re-create connections with the new credentials: set `maxLifetime` below the rotation interval.
