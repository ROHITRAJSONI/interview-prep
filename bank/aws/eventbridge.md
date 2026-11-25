# AWS EventBridge

## Q: EventBridge vs SNS vs SQS: when would you use each?
### Solution
- **SQS:** a queue for one consumer group. Buffering, load levelling, retries, DLQ. Pull-based.
- **SNS:** high-throughput pub/sub fan-out to many subscribers (SQS, Lambda, HTTP, email), with simple attribute filtering. Low latency.
- **EventBridge:** an event bus with **content-based routing rules** (filter on any JSON field), many native AWS/SaaS sources and 20+ target types, a schema registry, **archive & replay**, and **Scheduler** (cron/one-off). Latency and throughput are somewhat lower than SNS.

A common pattern is EventBridge rule → SQS → consumer: routing flexibility plus buffering and a DLQ per consumer.

## Q: How do retries and failures work for EventBridge targets?
### Solution
EventBridge retries delivery to a target with backoff for up to **24 hours / 185 attempts** by default. Both limits are configurable per target (retry policy). After that, the event is dropped unless you attach a **DLQ (an SQS queue) to the target**. The DLQ message includes error metadata.

Delivery is at-least-once, so consumers must be idempotent (dedupe on the event `id`). Use **archive & replay** to reprocess historical events after fixing a bug, and the `events:PutEvents` `FailedEntryCount` to detect publish failures on the producer side.
