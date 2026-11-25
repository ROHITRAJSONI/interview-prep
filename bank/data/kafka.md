# Apache Kafka

## Q: How does Kafka guarantee ordering, and how do consumer groups and rebalancing work?
### Solution
Ordering is guaranteed **only within a partition**. Messages with the same key go to the same partition (by key hash), so key by entity (e.g. `accountId`) when per-entity order matters. Changing the partition count changes the key mapping.

**Consumer groups:** each partition is assigned to exactly one consumer in the group, so parallelism ≤ number of partitions. Extra consumers sit idle. A **rebalance** happens when consumers join or leave, or exceed `max.poll.interval.ms` (processing too slow). Classic "eager" rebalancing stops the whole group. Use the **CooperativeStickyAssignor** (incremental) and **static membership** (`group.instance.id`) to avoid rebalance storms during rolling deploys.

## Q: Explain at-most-once, at-least-once and exactly-once in Kafka. How do you get exactly-once?
### Solution
- **At-most-once:** commit the offset *before* processing. A crash loses messages.
- **At-least-once** (the usual default): process, *then* commit. A crash causes reprocessing, so consumers must be idempotent.
- **Exactly-once:** the producer runs with `enable.idempotence=true` (the default since Kafka 3.0, with `acks=all`), which dedupes retries per partition. **Transactions** (`transactional.id`) atomically write output records *and* consumer offsets (`sendOffsetsToTransaction`). Downstream consumers use `isolation.level=read_committed`. Kafka Streams wraps all this as `processing.guarantee=exactly_once_v2`.

The catch: EOS only covers Kafka-to-Kafka. If the side effect is a DB write or an HTTP call, you still need an idempotent sink (upsert by key, dedupe table) or the outbox pattern.

## Q: Your consumer lag keeps growing. How do you troubleshoot it?
### Solution
1. **Measure:** lag per partition (Burrow, `kafka-consumer-groups --describe`, CloudWatch for MSK). Is it all partitions or one?
2. **One hot partition:** key skew. Fix the keying, or add salt to the key if strict ordering isn't required.
3. **All partitions:** slow processing. Profile the downstream DB/HTTP calls; batch the writes; process asynchronously within the partition while keeping per-key order.
4. **Scale out:** add consumers, up to the partition count; add partitions if needed (this breaks the key mapping).
5. **Rebalance loops:** processing exceeds `max.poll.interval.ms`, so the group keeps rebalancing and makes no progress. Lower `max.poll.records` or raise the interval.
6. **Poison messages:** a retry topic plus a DLT (Spring Kafka `DefaultErrorHandler` + `DeadLetterPublishingRecoverer`) so one bad record doesn't block the partition.
