# RabbitMQ

## Q: Kafka vs RabbitMQ: when would you pick each?
### Solution
**RabbitMQ** is a smart broker: flexible routing (direct, topic, fanout, headers exchanges), per-message acks, priorities, TTL, delayed messages, and request/reply. Messages are deleted once consumed. Good for **task queues and command-style work** with complex routing and low latency at moderate volume.

**Kafka** is a distributed **log**: messages are retained and **replayable**, multiple independent consumer groups can read the same data, it handles very high throughput, and it orders per partition. Good for **event streaming**, event sourcing, CDC, analytics pipelines and fan-out to many systems.

(RabbitMQ **Streams** and **quorum queues** narrow the gap, but the core models differ.)

## Q: How do you handle failed messages and guarantee delivery in RabbitMQ?
### Solution
- **Publisher side:** durable exchanges/queues + persistent messages + **publisher confirms**; `mandatory` flag/returns for unroutable messages.
- **Consumer side:** **manual acks** after successful processing; `basic.nack(requeue=false)` sends the message to a **dead-letter exchange (DLX)**. Don't requeue forever, or poison messages loop.
- **Retry with delay:** a retry queue with a TTL whose DLX points back to the main queue, or the delayed-message plugin. Count attempts via the `x-death` header.
- **Prefetch** (`basic.qos`) limits unacked messages per consumer, which balances load.
- Use **quorum queues** (Raft-replicated) instead of classic mirrored queues for HA.
