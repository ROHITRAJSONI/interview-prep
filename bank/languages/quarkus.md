# Quarkus

## Q: Why does Quarkus start so fast, and what are the trade-offs of native image?
### Solution
Quarkus moves work to **build time**: annotation scanning, CDI wiring (ArC), and config parsing all happen during the build and are recorded as bytecode, so the runtime does very little. In JVM mode that gives fast startup. In **native mode** (GraalVM/Mandrel) you get tens-of-ms startup and low RSS, which is ideal for Lambda and scale-to-zero.

Native trade-offs:
- Closed-world assumption: reflection, dynamic proxies and resources must be registered (`@RegisterForReflection`), and some libraries don't work.
- Long, memory-hungry builds; harder debugging.
- Peak throughput can be lower than a JIT-warmed JVM for long-running services.

Rule of thumb: native for Lambda/CLI/short-lived workloads, JVM mode for long-running high-throughput services.

## Q: How does Quarkus combine imperative and reactive code?
### Solution
Quarkus is built on Vert.x. RESTEasy Reactive endpoints run on the **event loop** if they return `Uni`/`Multi`, and on a **worker thread** if they return a plain type. You can force this with `@Blocking`/`@NonBlocking`, or use `@RunOnVirtualThread` on Java 21.

So you can write normal blocking JPA (Hibernate ORM) code in one endpoint and Hibernate Reactive / reactive messaging in another, in the same app. The pitfall is a blocking call inside a `Uni` pipeline on the event loop. Quarkus warns about it, so offload with `.emitOn(executor)` or mark the endpoint `@Blocking`.
