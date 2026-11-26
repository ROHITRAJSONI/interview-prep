-- Auto-pushed at 10:35 IST: model solution (no attempt pushed by 10:30 IST)

-- Schema + sample data (MySQL 8.0; also runs on SQLite >= 3.25 for sanity checks)
CREATE TABLE transactions (
  txn_id     INT PRIMARY KEY,
  account_id INT NOT NULL,
  amount     DECIMAL(12,2) NOT NULL,   -- +credit / -debit
  txn_ts     TIMESTAMP NOT NULL
);
CREATE INDEX idx_txn_acct_ts ON transactions (account_id, txn_ts, txn_id);

INSERT INTO transactions VALUES
 (1, 100,  500.00, '2026-01-01 09:00:00'),
 (2, 100, -200.00, '2026-01-02 10:00:00'),
 (3, 100, -400.00, '2026-01-03 11:00:00'),  -- balance -100: first overdraft
 (4, 100,  300.00, '2026-01-04 12:00:00'),
 (5, 100, -300.00, '2026-01-05 12:00:00'),  -- negative again
 (6, 200,  100.00, '2026-01-01 09:00:00'),
 (7, 200,  -50.00, '2026-01-02 09:00:00'),
 (8, 300,  -10.00, '2026-01-01 08:00:00'),  -- negative on first txn
 (9, 300,   10.00, '2026-01-01 08:00:00');  -- same ts, tie broken by txn_id

-- Per account: first txn where running balance < 0, its balance, and
-- the number of txns that left the account overdrawn.
WITH running AS (
  SELECT account_id, txn_id, txn_ts, amount,
         SUM(amount) OVER (PARTITION BY account_id
                           ORDER BY txn_ts, txn_id
                           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS balance
  FROM transactions
),
flagged AS (
  SELECT r.*,
         ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY txn_ts, txn_id) AS rn
  FROM running r
  WHERE balance < 0
)
SELECT f.account_id, f.txn_id AS first_overdraft_txn, f.txn_ts AS first_overdraft_ts,
       f.balance AS balance_after,
       (SELECT COUNT(*) FROM running x
         WHERE x.account_id = f.account_id AND x.balance < 0) AS overdrawn_txn_count
FROM flagged f
WHERE f.rn = 1
ORDER BY f.account_id;
