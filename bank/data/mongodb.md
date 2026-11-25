# MongoDB

## Q: Embedding vs referencing in MongoDB schema design: how do you decide?
### Solution
**Embed** when the data is read together, belongs to the parent (1:1 or 1:few), and doesn't grow without bound: e.g. an order with its line items and shipping address. You get one read and atomic updates on a single document.
**Reference** when the relation is 1:many-unbounded or many:many, the child is accessed on its own, or embedding would push the document toward the **16 MB limit** (e.g. a customer's transactions).

Useful patterns: **subset** (embed the latest N items, reference the rest), **extended reference** (copy a few frequently-read fields), **bucket** (time-series grouping). Design for the query patterns, like with DynamoDB.

## Q: How do indexes and transactions work in MongoDB?
### Solution
Indexes are B-trees: single-field, **compound** (follow the **ESR rule**: Equality, then Sort, then Range fields), multikey (arrays), TTL, partial, text. Check them with `explain("executionStats")`: you want `IXSCAN` rather than `COLLSCAN`, and `totalDocsExamined` close to `nReturned`.

Single-document writes are always atomic. **Multi-document ACID transactions** have been supported since 4.0 (replica sets) and 4.2 (sharded clusters), but they cost performance and have a 60-second default limit. If you need them often, the schema probably should embed. Use `writeConcern: majority` + `readConcern: majority` for durable reads and writes.
