# Spring Cloud

## Q: Which Spring Cloud components have you used, and what replaced the Netflix stack?
### Solution
| Concern | Old (Netflix) | Current |
|---|---|---|
| Client load balancing | Ribbon | Spring Cloud LoadBalancer |
| Circuit breaker | Hystrix | Spring Cloud CircuitBreaker + **Resilience4j** |
| Gateway | Zuul 1 | **Spring Cloud Gateway** (reactive, Netty) |
| Discovery | Eureka | Eureka still works; on AWS often ECS Service Connect / Cloud Map, or K8s DNS |
| Config | — | Spring Cloud Config Server, or AWS Parameter Store/AppConfig via `spring-cloud-aws` |
| Declarative HTTP | Feign | OpenFeign, or Spring 6 `@HttpExchange` interfaces |

Senior point: on AWS/K8s much of this moves to the platform (service discovery, load balancing, config). Only pull in Spring Cloud pieces the platform doesn't already give you.

## Q: How does Spring Cloud Config refresh work without restarting the service?
### Solution
Beans annotated `@RefreshScope` are lazily recreated after a refresh event. Hitting `POST /actuator/refresh` re-reads the config sources and rebinds `@ConfigurationProperties`. To refresh a whole fleet, use **Spring Cloud Bus** (Kafka/RabbitMQ): one `/actuator/busrefresh` call broadcasts to all instances.

Caveats: `@Value` fields on non-refresh-scoped singletons don't change; connection pools and other stateful beans may need a restart anyway. Treat dynamic config as feature flags and tunables, not as schema or infrastructure changes.
