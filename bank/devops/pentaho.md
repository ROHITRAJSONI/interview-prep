# Pentaho

## Q: What's the difference between a Pentaho transformation and a job, and how do you run them in production?
### Solution
In Pentaho Data Integration (PDI / Kettle):
- A **transformation (`.ktr`)** is a data-flow: **steps run in parallel**, streaming rows through (Table Input → Lookup → Filter → Table Output).
- A **job (`.kjb`)** is control-flow: **entries run sequentially**, orchestrating transformations, file checks, SQL, email, with success/failure hops.

Production: run headless with **Pan** (transformations) and **Kitchen** (jobs) from Control-M or cron. Pass parameters/variables (`-param:RUN_DATE=…`), use `kettle.properties` per environment, store in a repository/Git, and rely on exit codes for scheduler failure detection.

## Q: How do you make a Pentaho ETL load performant and restartable?
### Solution
- Push the heavy work into the DB (SQL in Table Input; bulk loader steps) instead of row-by-row lookups. Use **Stream Lookup / Database Join with caching**.
- Tune the **commit size** and the number of step copies (parallelism); use the bulk loaders for Oracle/MySQL.
- **Incremental loads** with a watermark (last-modified timestamp or ID) stored in a control table.
- **Restartability:** load into staging, then do an atomic switch/merge; log every run (job/transformation logging tables) with status, so a rerun starts from the failed batch; make the loads idempotent (upserts via Insert/Update or Merge).
- Error-handling hops route bad rows to a reject table instead of failing the whole load.
