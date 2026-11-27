import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

/** Standalone model of an SQS-triggered Lambda handler with partial batch failure + idempotency. */
public class Solution {
    record SqsMessage(String messageId, String body) {}
    record BatchResponse(List<String> batchItemFailures) {}

    /** Stand-in for a DynamoDB table with conditional put (attribute_not_exists). */
    static class IdempotencyStore {
        enum State { IN_PROGRESS, DONE }
        private final ConcurrentHashMap<String, State> map = new ConcurrentHashMap<>();
        /** @return true if this caller acquired the key (first time). */
        boolean tryStart(String key) { return map.putIfAbsent(key, State.IN_PROGRESS) == null; }
        void complete(String key) { map.put(key, State.DONE); }
        void release(String key) { map.remove(key, State.IN_PROGRESS); } // allow retry after failure
    }

    interface PaymentProcessor { void process(String paymentId, long cents); }

    static class Handler {
        private final IdempotencyStore store;
        private final PaymentProcessor processor;
        Handler(IdempotencyStore s, PaymentProcessor p) { store = s; processor = p; }

        BatchResponse handle(List<SqsMessage> batch) {
            List<String> failed = new ArrayList<>();
            boolean poisoned = false; // for FIFO: after first failure, fail the rest to keep ordering
            for (SqsMessage m : batch) {
                if (poisoned) { failed.add(m.messageId()); continue; }
                try {
                    processOne(m);
                } catch (Exception e) {
                    failed.add(m.messageId());
                    poisoned = true; // remove this line for standard queues (independent messages)
                }
            }
            return new BatchResponse(failed);
        }

        private void processOne(SqsMessage m) {
            String[] parts = m.body().split(",");           // "paymentId,cents"
            if (parts.length != 2) throw new IllegalArgumentException("bad payload " + m.messageId());
            String paymentId = parts[0];
            long cents = Long.parseLong(parts[1]);
            if (!store.tryStart(paymentId)) return;         // duplicate delivery -> treat as success
            try {
                processor.process(paymentId, cents);
                store.complete(paymentId);
            } catch (RuntimeException e) {
                store.release(paymentId);
                throw e;
            }
        }
    }

    public static void main(String[] args) {
        Set<String> processed = new LinkedHashSet<>();
        Handler h = new Handler(new IdempotencyStore(), (id, c) -> {
            if (id.equals("p3")) throw new IllegalStateException("downstream down");
            processed.add(id);
        });
        List<SqsMessage> batch = List.of(
            new SqsMessage("m1", "p1,100"), new SqsMessage("m2", "p1,100"),
            new SqsMessage("m3", "p3,300"), new SqsMessage("m4", "p4,400"));
        BatchResponse r = h.handle(batch);
        System.out.println("failed=" + r.batchItemFailures() + " processed=" + processed);
        if (!r.batchItemFailures().equals(List.of("m3", "m4")) || !processed.equals(Set.of("p1")))
            throw new AssertionError();
    }
}
