# Vert.x

## Q: Explain Vert.x's event loop model and the golden rule.
### Solution
Vert.x runs a small number of **event-loop threads** (default 2 × cores). Each verticle is bound to one event loop, so its handlers are never called concurrently. That means no locking inside a verticle. It's the multi-reactor pattern.

**Golden rule: never block the event loop.** A blocking JDBC call or `Thread.sleep` stalls every handler on that loop, and Vert.x logs `BlockedThreadChecker` warnings. For blocking work use `vertx.executeBlocking(...)` or deploy a **worker verticle** (or virtual-thread verticles in Vert.x 4.5+/5).

The **event bus** is used for communication between verticles: point-to-point, publish/subscribe, and request-reply, and it can be clustered.

## Q: When would you choose Vert.x over Spring Boot (WebFlux or MVC)?
### Solution
Choose Vert.x when you need very high concurrency with low memory: gateways, proxies, streaming/WebSocket fan-out, IoT ingestion. It's a toolkit, not a framework. It has fast startup, a tiny footprint, and no DI or magic.

Trade-offs: the callback/Future style is harder to read and debug, the ecosystem is smaller (security, data access, observability are more DIY), and it's harder to hire for. Spring WebFlux gives a similar non-blocking model with the Spring ecosystem. With **Java 21 virtual threads**, plain Spring MVC now handles a lot of high-concurrency I/O workloads that used to need reactive frameworks.
