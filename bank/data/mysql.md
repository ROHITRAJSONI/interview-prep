# MySQL

## Q: A query is slow in production. How do you diagnose and fix it?
### Solution
1. Find it: slow query log / Performance Insights / `performance_schema`.
2. `EXPLAIN` (or `EXPLAIN ANALYZE` in 8.0): look for `type=ALL` (full scan), large `rows` estimates, `Using filesort`, `Using temporary`.
3. Fixes:
   - **Composite index** in the right column order: equality columns first, then the range or sort column. `(customer_id, created_at)` serves `WHERE customer_id=? ORDER BY created_at DESC`.
   - A **covering index** avoids table lookups.
   - Avoid functions on indexed columns (`DATE(created_at)=…`); rewrite as a range.
   - Replace `OFFSET` pagination with **keyset pagination** (`WHERE id < :last ORDER BY id DESC LIMIT 50`).
   - Watch for implicit type conversion (comparing a string column to a number disables the index).
4. Re-check: stale statistics → `ANALYZE TABLE`.

## Q: Explain InnoDB isolation levels and what REPEATABLE READ actually protects against.
### Solution
InnoDB's default is **REPEATABLE READ**. Plain `SELECT`s read a consistent MVCC snapshot taken at the first read, so there are no dirty or non-repeatable reads. *Locking* reads (`SELECT … FOR UPDATE`, UPDATE/DELETE) use **next-key locks** (record + gap) to block phantom inserts in the scanned range.

Gotcha: a snapshot read and a locking read in the same transaction can see different data. Gap locks also cause unexpected deadlocks under high write concurrency, which is why some teams use **READ COMMITTED** (no gap locks, less deadlocking; Oracle's default too) and handle consistency with explicit `FOR UPDATE` or optimistic version columns.
