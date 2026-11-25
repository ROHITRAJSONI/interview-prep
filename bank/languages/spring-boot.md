# Spring Boot

## Q: How does Spring Boot auto-configuration work, and how do you debug or override it?
### Solution
`@SpringBootApplication` includes `@EnableAutoConfiguration`. Boot loads candidate classes listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Boot 3; `spring.factories` in Boot 2). Each one is guarded by conditions: `@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty`, and so on. Because of `@ConditionalOnMissingBean`, **defining your own bean overrides the default**.

Debug it by running with `--debug` (or `debug=true`) to get the **Condition Evaluation Report**, or check the `/actuator/conditions` endpoint. Disable one with `@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)` or `spring.autoconfigure.exclude`.

## Q: `@Transactional` isn't rolling back, or isn't applied at all. What are the usual causes?
### Solution
1. **Self-invocation:** calling a `@Transactional` method from the same class skips the proxy. Move it to another bean or inject self.
2. **Non-public method** (with proxy-based AOP before Spring 6, which only applies it to public methods).
3. **Checked exceptions:** rollback by default is only for `RuntimeException`/`Error`. Use `rollbackFor = Exception.class`.
4. **Swallowed exceptions:** a `catch` without a rethrow means the commit happens.
5. The bean isn't Spring-managed (created with `new`).
6. Wrong transaction manager when there are multiple datasources.

Also know **propagation**: `REQUIRES_NEW` suspends the outer transaction (useful for audit logs), and `NESTED` uses savepoints.

## Q: How would you make a Spring Boot microservice production-ready?
### Solution
- **Observability:** Actuator health/readiness/liveness probes, Micrometer metrics to Prometheus/CloudWatch, distributed tracing (Micrometer Tracing / OpenTelemetry), structured JSON logs with a correlation ID in MDC.
- **Resilience:** timeouts on every outbound call, Resilience4j retry + circuit breaker + bulkhead, connection pool sizing (Hikari).
- **Config & secrets:** externalized config, profiles, secrets from Secrets Manager / Parameter Store, never baked into the jar.
- **Graceful shutdown:** `server.shutdown=graceful` plus a timeout, so in-flight requests finish when ECS/K8s drains the task.
- **Security:** Spring Security, OAuth2 resource server (JWT), input validation (`@Valid`), dependency CVE scanning.
- **API hygiene:** versioning, consistent error format (`ProblemDetail` in Boot 3), idempotency keys for POSTs that clients retry.
