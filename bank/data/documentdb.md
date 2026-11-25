# Amazon DocumentDB

## Q: Is DocumentDB the same as MongoDB? What do you watch out for when migrating?
### Solution
No. DocumentDB is AWS's own engine that implements the **MongoDB wire protocol and API** (compatible with 3.6/4.0/5.0), built on Aurora-style storage: compute is separate from storage, which keeps 6 copies across 3 AZs, and you can have up to 15 read replicas.

Migration gotchas:
- **Not every operator/feature is supported.** Some aggregation stages, `$where`/JavaScript, certain index types, and change-stream differences. Run AWS's compatibility tool against your queries.
- **Transactions** and change streams have limits/configuration (change streams must be enabled per collection, with retention).
- Connect via the **cluster endpoint** for writes and the **reader endpoint** with `readPreference=secondaryPreferred` for reads; TLS on by default.
- It runs **only inside a VPC**; there's no public endpoint.
- Use **AWS DMS** for the migration (full load + CDC).

## Q: How do you scale reads and handle failover in DocumentDB?
### Solution
Add **replica instances** (up to 15). They share the cluster storage volume, so replica lag is usually in milliseconds. Route reads to replicas through the reader endpoint with `readPreference=secondaryPreferred`. On primary failure a replica is promoted, usually in **under ~30 seconds**. The cluster endpoint DNS moves to the new primary, so drivers should connect with `replicaSet=rs0`. DocumentDB **doesn't support MongoDB retryable writes**, so set `retryWrites=false` in the connection string and retry idempotent writes in the app (with backoff) during the failover window. Set failover priority tiers to control which replica gets promoted.
