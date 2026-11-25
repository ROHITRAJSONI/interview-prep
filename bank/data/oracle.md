# Oracle

## Q: How would you load or update millions of rows in Oracle efficiently from Java?
### Solution
- **JDBC batching:** `addBatch`/`executeBatch` in chunks of 500–5,000, with `rewriteBatchedStatements` not applicable (that's MySQL); Oracle batches natively. Commit per chunk, not per row.
- Set-based SQL instead of row-by-row: `MERGE INTO … USING staging` for upserts, `INSERT /*+ APPEND */ … SELECT` (direct-path) for bulk loads.
- Load into a **staging table** (SQL*Loader / external tables for files), then transform in SQL.
- Spring Batch with a chunk-oriented step, plus partitioning for parallelism.
- Disable or rebuild non-essential indexes for huge loads; gather stats afterwards (`DBMS_STATS`).
- Watch undo/redo volume and lock duration. Commit in chunks so a failure can restart from a checkpoint.

## Q: What's the difference between an index range scan and a full table scan, and when does Oracle prefer the full scan?
### Solution
An **index range scan** walks the B-tree for matching keys, then does a `TABLE ACCESS BY ROWID` for each row: good when the query is selective (a small fraction of the rows). A **full table scan** reads all blocks using multiblock I/O. That's cheaper when you need a large fraction of the table, or the index clustering factor is poor (rows scattered across blocks).

The cost-based optimizer chooses using **statistics**, so stale stats lead to bad plans. Tools: `EXPLAIN PLAN` / `DBMS_XPLAN.DISPLAY_CURSOR` (actual vs estimated rows), AWR/ASH reports, SQL Plan Baselines to pin a good plan. Bind variable peeking and adaptive cursor sharing explain "fast for one customer, slow for another".
