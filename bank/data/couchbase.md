# Couchbase / CouchDB

## Q: Couchbase vs CouchDB: they sound alike, how do they differ?
### Solution
- **Couchbase Server:** a distributed document DB with a **memory-first architecture** (an integrated cache, the memcached heritage), key-value ops in sub-milliseconds, **SQL++ (N1QL)** queries, Full-Text Search, Eventing, Analytics, and multi-dimensional scaling (you scale data, query and index services separately). Cross-datacenter replication via XDCR.
- **Apache CouchDB:** an HTTP/JSON database with MVCC revisions, **multi-master replication** and offline-first sync (PouchDB in mobile/browser apps). Queries use MapReduce views or Mango.

They share history (Couchbase came from a merger with CouchOne), but they're separate products. Couchbase targets high-throughput caching and operational workloads; CouchDB targets sync/replication-centric apps.

## Q: How do you handle concurrent updates in Couchbase?
### Solution
**Optimistic locking with CAS:** every document has a CAS value that changes on each mutation. Read the document with its CAS, then `replace(id, doc, ReplaceOptions.replaceOptions().cas(cas))`. If someone else wrote in between, you get a `CasMismatchException`; re-read and retry. **Pessimistic:** `getAndLock` (max 30 s), but that hurts throughput.

For multi-document atomicity use **Couchbase ACID transactions** (6.5+). Use durability levels (`MAJORITY`, `PERSIST_TO_MAJORITY`) when a write must survive a node failure before it's acknowledged.
