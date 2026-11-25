# Multithreading & Concurrency

## Q: How do you size a ThreadPoolExecutor, and what happens when it's saturated?
### Solution
Task submission order: if there are fewer than `corePoolSize` threads, start a new thread; otherwise **queue** the task; if the queue is full and there are fewer than `maxPoolSize` threads, start a new thread; otherwise apply the **RejectedExecutionHandler** (Abort, CallerRuns, Discard, DiscardOldest).

Gotcha: with an **unbounded `LinkedBlockingQueue`** (which `Executors.newFixedThreadPool` uses), `maxPoolSize` is never reached and the queue can grow until OOM. Use a bounded queue plus `CallerRunsPolicy` for backpressure.

Sizing: CPU-bound work ≈ number of cores. I/O-bound work ≈ `cores × (1 + wait/compute)`. Measure, give pools meaningful thread names, and monitor queue depth and active count. On Java 21, **virtual threads** (`Executors.newVirtualThreadPerTaskExecutor()`) remove most pool sizing for blocking I/O, but limit concurrency to downstream resources with a `Semaphore`.

## Q: Write code that runs three remote calls in parallel, with a timeout, and combines the results.
### Solution
```java
ExecutorService io = Executors.newFixedThreadPool(16);

CompletableFuture<Account> acc = supplyAsync(() -> accountClient.get(id), io);
CompletableFuture<List<Txn>> txns = supplyAsync(() -> txnClient.recent(id), io);
CompletableFuture<Risk> risk = supplyAsync(() -> riskClient.score(id), io)
        .completeOnTimeout(Risk.UNKNOWN, 300, MILLISECONDS);   // optional dependency → fallback

Summary s = CompletableFuture.allOf(acc, txns, risk)
        .orTimeout(2, SECONDS)
        .thenApply(v -> new Summary(acc.join(), txns.join(), risk.join()))
        .join();
```
Points to say out loud: pass a **dedicated executor**, because the default common ForkJoinPool is bad for blocking I/O. Use `orTimeout`/`completeOnTimeout` (Java 9+). Handle errors with `exceptionally`/`handle`. Propagate MDC/trace context into the async tasks.

## Q: What is a deadlock, and how do you detect and prevent one?
### Solution
Four conditions must all hold: mutual exclusion, hold-and-wait, no preemption, and **circular wait**. Classic case: thread 1 locks A then B, thread 2 locks B then A.

**Prevent:** a global lock-ordering rule (e.g. always lock the lower account ID first in a transfer), `tryLock(timeout)` with back-off (`ReentrantLock`), holding locks for less time, and not calling foreign code while holding a lock.
**Detect:** thread dump (`jstack`, `jcmd <pid> Thread.print`), which reports "Found one Java-level deadlock". Also `ThreadMXBean.findDeadlockedThreads()` for monitoring. Databases detect DB-level deadlocks themselves and abort one transaction, so retry it.
