// Auto-pushed at 10:35 IST: model solution (no attempt pushed by 10:30 IST)

import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;

/** Idempotent payment endpoint logic: same Idempotency-Key => same result, executed once. */
public class Solution {

    record Response(int status, String body) {}

    /** Stored state of a key: fingerprint of request + a future of the outcome. */
    private record Entry(String fingerprint, CompletableFuture<Response> result, long createdNanos) {}

    static class IdempotencyService {
        private final ConcurrentHashMap<String, Entry> store = new ConcurrentHashMap<>();
        private final long ttlNanos;

        IdempotencyService(Duration ttl) { this.ttlNanos = ttl.toNanos(); }

        Response execute(String key, String requestBody, Supplier<Response> action) {
            String fp = Integer.toHexString(Objects.hash(requestBody)); // use SHA-256 in prod
            long now = System.nanoTime();
            Entry mine = new Entry(fp, new CompletableFuture<>(), now);

            // atomic claim; also evicts an expired entry
            Entry existing = store.compute(key, (k, cur) ->
                    (cur == null || now - cur.createdNanos > ttlNanos) ? mine : cur);

            if (existing != mine) {
                if (!existing.fingerprint().equals(fp)) {
                    return new Response(422, "Idempotency-Key reused with different payload");
                }
                try {                       // concurrent duplicate waits for the first call
                    return existing.result().get(5, TimeUnit.SECONDS);
                } catch (TimeoutException e) {
                    return new Response(409, "Original request still in progress");
                } catch (InterruptedException | ExecutionException e) {
                    Thread.currentThread().interrupt();
                    return new Response(500, "Failed waiting for original");
                }
            }
            try {
                Response r = action.get();
                mine.result().complete(r);
                if (r.status() >= 500) store.remove(key, mine); // don't cache transient failures
                return r;
            } catch (RuntimeException ex) {
                store.remove(key, mine);     // allow retry
                mine.result().complete(new Response(500, "error"));
                throw ex;
            }
        }
    }

    public static void main(String[] args) throws Exception {
        IdempotencyService svc = new IdempotencyService(Duration.ofHours(24));
        AtomicInteger charges = new AtomicInteger();
        Supplier<Response> charge = () -> {
            try { Thread.sleep(100); } catch (InterruptedException ignored) {}
            return new Response(201, "charge-" + charges.incrementAndGet());
        };
        ExecutorService pool = Executors.newFixedThreadPool(8);
        var futures = new java.util.ArrayList<Future<Response>>();
        for (int i = 0; i < 8; i++) futures.add(pool.submit(() -> svc.execute("k1", "{amt:10}", charge)));
        for (var f : futures) System.out.println(f.get());
        System.out.println("charges executed = " + charges.get());       // 1
        System.out.println(svc.execute("k1", "{amt:99}", charge));        // 422
        pool.shutdown();
    }
}
