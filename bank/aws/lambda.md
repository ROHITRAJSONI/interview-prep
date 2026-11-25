# AWS Lambda

## Q: How do you reduce cold starts for a Java Lambda?
### Solution
- **SnapStart** (Java 11+ on Corretto): Lambda snapshots the initialized execution environment at publish time and restores it on cold start. Use runtime hooks (CRaC `beforeCheckpoint`/`afterRestore`) to refresh anything that must be unique per instance: random seeds, connections, cached credentials.
- **Provisioned concurrency** for strict latency SLAs (you pay for idle capacity).
- Do the heavy init **outside the handler** (SDK clients, config) so warm invocations reuse it.
- Trim the deployment: avoid full Spring context scanning, or use Quarkus/Micronaut or GraalVM native; use the AWS SDK v2 with the `UrlConnection`/CRT HTTP client.
- More memory gives proportionally more CPU, which often reduces both latency *and* cost.
- `JAVA_TOOL_OPTIONS=-XX:+TieredCompilation -XX:TieredStopAtLevel=1` speeds up startup.

## Q: A Lambda consumes from SQS. How do you handle failures and partial batch failures?
### Solution
The event source mapping polls SQS and invokes the function with a batch. If the function **throws**, the *whole batch* becomes visible again after the visibility timeout. That reprocesses the successful messages too, so handlers must be **idempotent**.

Better: enable `ReportBatchItemFailures` and return `batchItemFailures` with only the failed message IDs. Configure a **redrive policy** (`maxReceiveCount`) to a **DLQ**, and set the queue's visibility timeout to at least 6× the function timeout. Use `MaximumConcurrency` on the mapping to protect downstream databases. For FIFO queues, a failure blocks its message group until that message is handled.
