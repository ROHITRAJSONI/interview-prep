# Microservices Architecture

## Q: How do you keep data consistent across microservices without distributed transactions?
### Solution
Use a **Saga**: a sequence of local transactions, each with a **compensating action** (e.g. `reserveFunds` → `releaseFunds`).
- **Choreography:** services react to each other's events. Coupling is loose, but the flow is hard to see end to end.
- **Orchestration:** a central orchestrator (Step Functions, Temporal, or a state machine service) drives the steps. Easier to reason about and monitor.

Make publishing reliable with the **Transactional Outbox**: write the business row and an outbox row in the same DB transaction, and a relay (Debezium CDC or a poller) publishes outbox rows to Kafka. That avoids the dual-write problem. Consumers are **idempotent** (dedupe table keyed on event ID). Accept eventual consistency, and design the UI and APIs for pending states.

## Q: Service A calls B, and B is slow or down. How do you stop it from cascading?
### Solution
- **Timeouts** on every call: connect and read, tuned to B's p99, never infinite.
- **Retries** only for idempotent operations, with exponential backoff, jitter and a retry budget, or retries amplify the outage.
- **Circuit breaker** (Resilience4j): after a failure-rate threshold, fail fast for a while, then let half-open probe calls through.
- **Bulkhead:** a separate thread pool / semaphore per dependency, so B can't exhaust A's threads.
- **Fallbacks:** cached or default responses, or degrade the feature.
- **Async decoupling:** a queue between A and B where the user doesn't need an immediate answer.
- **Load shedding / rate limiting** at the edge. Monitor with RED metrics per dependency.

## Q: How do you decide service boundaries, and when are microservices the wrong choice?
### Solution
Draw boundaries around **business capabilities / DDD bounded contexts**. Each service owns its data (no shared database), changes for one reason, and can be deployed independently. Smell tests: services that always deploy together, chatty synchronous call chains, or a shared schema mean the boundaries are wrong (a distributed monolith).

They're the wrong choice for a small team, an unclear domain, or when you don't have mature CI/CD, observability and on-call. The operational cost (network failures, eventual consistency, distributed debugging) is real. A **modular monolith** with clear module boundaries is often the better start; extract services when scaling or team independence actually demands it.
