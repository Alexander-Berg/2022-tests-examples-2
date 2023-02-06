-- On vshard 0 we started replicating the earliest rollup
INSERT INTO ba_testsuite_00.balance_replication_chunks
(
    last_journal_id,
    last_account_id,
    last_accrued_at,
    count
)
VALUES
(
    10000,
    10000,
    '2020-01-10 08:00:00.000000'::timestamp,
    1023
);

-- On vshard 2 we started replicating some rollup that isn't there
INSERT INTO ba_testsuite_02.balance_replication_chunks
(
    last_journal_id,
    last_account_id,
    last_accrued_at,
    count
)
VALUES
(
    10002,
    10002,
    '2020-01-10 08:00:00.000000'::timestamp,
    1024
);
