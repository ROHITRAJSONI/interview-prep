# Java (8 / 11 / 17)

## Q: What changed between Java 8, 11 and 17 that you actually use day to day?
### Solution
- **Java 8:** lambdas, Streams, `Optional`, `CompletableFuture`, `java.time`, default methods on interfaces.
- **Java 11 (LTS):** `var` in lambdas (`var` itself arrived in 10), `String` helpers (`isBlank`, `strip`, `lines`, `repeat`), `Files.readString/writeString`, the standard `HttpClient`, single-file `java Foo.java` launch. Java EE and CORBA modules were removed, so JAXB/JAX-WS became explicit dependencies, which is a classic migration break.
- **Java 17 (LTS):** records, sealed classes, pattern matching for `instanceof`, switch expressions, text blocks, helpful NPE messages. Strong encapsulation of JDK internals (`--illegal-access` gone) breaks old libraries that used reflection on internals.

Senior angle: mention the **migration** work. You bump Lombok, Mockito and ByteBuddy, add the JAXB deps, and fix `--add-opens` issues. Spring Boot 3 requires Java 17+ and moves `javax.*` to `jakarta.*`.

## Q: How does HashMap work internally, and what changed in Java 8?
### Solution
An array of buckets. `hash(key)` spreads the high bits (`h ^ (h >>> 16)`), and the index is `(n-1) & hash`. A collision chains entries in a linked list. **Since Java 8**, a bucket with ≥8 entries (when the table has ≥64 slots) is **treeified** into a red-black tree, so the worst case drops from O(n) to O(log n). Default load factor is 0.75, and on resize the capacity doubles. Each entry either stays at index `i` or moves to `i + oldCap`, so nothing needs rehashing from scratch.

Pitfalls:
- Mutable keys: changing a field used in `hashCode()` after insertion "loses" the entry.
- `equals`/`hashCode` contract: equal objects must have equal hashes.
- Not thread-safe. Concurrent resize in Java 7 could create a cycle. Use `ConcurrentHashMap`, which uses CAS plus per-bin locking (no segments since Java 8).

## Q: Explain the Java memory model's happens-before and when `volatile` is enough.
### Solution
Happens-before guarantees that writes before an action are visible to reads after it. Edges include: an unlock happens-before a later lock on the same monitor, a `volatile` write happens-before subsequent reads of that variable, `Thread.start()` happens-before the thread's actions, and a thread's actions happen-before another thread's `join()` returns.

`volatile` gives **visibility and ordering, not atomicity**. It's enough for a single writer and many readers (a `running` flag, or safe publication of an immutable object). It's **not** enough for `count++` (read-modify-write); use `AtomicInteger`/`LongAdder` or a lock there.

```java
private volatile boolean running = true;   // fine
private volatile int count;                // count++ is still a race
```

## Q: Streams: what's the difference between intermediate and terminal operations, and when would you avoid parallel streams?
### Solution
Intermediate ops (`map`, `filter`, `sorted`) are lazy and return a new stream. Nothing runs until a terminal op (`collect`, `forEach`, `reduce`, `findFirst`) is called. Short-circuiting ops (`findFirst`, `anyMatch`, `limit`) can stop early.

Avoid `parallelStream()` when:
- the work is I/O-bound or small (the split/merge overhead dominates),
- the source splits badly (`LinkedList`, `Stream.iterate`),
- you're inside a server. It uses the shared **common ForkJoinPool**, so one heavy request can starve the others,
- the ops have side effects or need ordering (`forEachOrdered` kills the benefit).

Use a dedicated executor with `CompletableFuture` for concurrent I/O instead.
