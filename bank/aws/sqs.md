# AWS SQS

## Q: Standard vs FIFO queues, and how do you achieve exactly-once processing?
### Solution
**Standard:** nearly unlimited throughput, at-least-once delivery, best-effort ordering. **FIFO:** strict ordering *per `MessageGroupId`*, deduplication within a 5-minute window (`MessageDeduplicationId` or content-based), and lower throughput (300 TPS, or 3,000 with batching; high-throughput mode goes higher).

FIFO dedup only covers duplicate *sends*. Processing is still at-least-once, because a consumer can crash after doing the work but before deleting the message. Real exactly-once *effects* need an **idempotent consumer**: a processed-message table with a conditional write (DynamoDB `attribute_not_exists`), or a business key with a unique constraint, inside the same transaction as the side effect.

## Q: Explain visibility timeout, long polling and DLQs, and the common misconfigurations.
### Solution
- **Visibility timeout:** after a receive, the message is hidden for N seconds. If it isn't deleted in time, it reappears, which causes duplicates. Set it longer than the worst-case processing time, or extend it with `ChangeMessageVisibility` for long jobs.
- **Long polling:** `WaitTimeSeconds` up to 20 cuts empty receives and cost.
- **DLQ:** a redrive policy with `maxReceiveCount`. Messages that keep failing go there instead of looping forever. Alarm on DLQ depth and use **DLQ redrive** to replay them after a fix.

Misconfigurations: visibility timeout shorter than the Lambda timeout; no DLQ, so poison messages loop; DLQ retention shorter than the source queue's; a FIFO queue with a standard DLQ (a FIFO queue needs a FIFO DLQ).
