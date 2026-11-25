# DynamoDB

## Q: How do you design a DynamoDB table? Walk through partition key choice and single-table design.
### Solution
Start from the **access patterns**, not the entities. List every query first.
- **Partition key:** high cardinality and evenly accessed (e.g. `customerId`), so no hot partitions. Each partition handles about 3,000 RCU / 1,000 WCU.
- **Sort key:** enables range queries and hierarchy, e.g. `PK=CUST#123`, `SK=ORDER#2026-11-25#9f3`, and `begins_with(SK,'ORDER#')` gives all orders.
- **GSIs** for alternative access patterns (eventually consistent, with their own capacity). Use sparse indexes for "only items with attribute X".
- **Single-table design** stores multiple entity types in one table, so one query fetches related items together. The trade-off is that it's harder to evolve and to run ad-hoc analytics on, so export to S3/Athena for those.

## Q: How do you implement optimistic locking and transactions in DynamoDB?
### Solution
**Optimistic locking:** keep a `version` attribute and write with a `ConditionExpression: version = :expected`, incrementing the version. A conflict throws `ConditionalCheckFailedException`; re-read and retry. The Enhanced Client's `@DynamoDbVersionAttribute` does this for you.

**Transactions:** `TransactWriteItems` gives all-or-nothing across up to 100 items/tables, with condition checks (e.g. debit one account only if `balance >= :amt` and credit another). It costs 2× the WCUs and can fail on conflicts (`TransactionCanceledException`). Use a `ClientRequestToken` for idempotent retries.

## Q: Query vs Scan, and how do you handle pagination?
### Solution
`Query` targets one partition key (plus optional sort-key conditions) and reads only the matching items. `Scan` reads the **whole table** and filters afterwards; you still pay for every item read. Avoid Scan in request paths. If you need it for jobs, use parallel scan with `Segment`/`TotalSegments`.

Both return at most 1 MB per call. Continue with `LastEvaluatedKey` → `ExclusiveStartKey`. Note: `FilterExpression` is applied **after** the read, so a page can come back with 0 items while `LastEvaluatedKey` is still set. Keep paginating. Return an opaque encoded cursor to API clients rather than page numbers.
