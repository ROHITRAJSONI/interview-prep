# Design Patterns

## Q: Which design patterns have you used in real projects (not textbook), and why?
### Solution
Give concrete examples:
- **Strategy:** a different fee/validation/report-generation rule per product or regulator, selected from a `Map<Type, Strategy>` of Spring beans. Removes big `switch` blocks, and each strategy is testable on its own.
- **Template Method:** a base batch/report job with fixed steps (`read → validate → transform → write`) and per-report hooks. Spring's `JdbcTemplate` is the same idea.
- **Builder:** immutable request/DTO objects with many optional fields (Lombok `@Builder`, records).
- **Factory:** creating clients/parsers by message type.
- **Decorator:** adding caching/metrics/retry around a repository or client without touching it. Spring AOP proxies are decorators.
- **Observer / pub-sub:** Spring `ApplicationEvent`s, Kafka.
- **Chain of Responsibility:** validation pipelines, servlet filters, Spring Security's filter chain.

## Q: Implement a thread-safe singleton. Which approach is best?
### Solution
```java
// 1. Enum: serialization- and reflection-safe (Effective Java's recommendation)
public enum Config { INSTANCE; }

// 2. Holder idiom: lazy and thread-safe through class-loading guarantees, no locking
public final class Registry {
    private Registry() {}
    private static class Holder { static final Registry I = new Registry(); }
    public static Registry get() { return Holder.I; }
}

// 3. Double-checked locking: needs volatile, or it's broken (partially constructed object)
private static volatile Cache instance;
static Cache get() {
    if (instance == null) synchronized (Cache.class) {
        if (instance == null) instance = new Cache();
    }
    return instance;
}
```
Senior point: in Spring apps, let the container manage singleton scope; hand-rolled singletons hurt testability.
