INSERT INTO ba_testsuite_00.balance_replication_chunks
(
    last_accrued_at,
    last_account_id,
    count,
    created,
    updated
)
VALUES
( -- t2i2
    '2019-01-01 11:11:11.000000'::TIMESTAMP,
    22220110000,
    4,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
);
