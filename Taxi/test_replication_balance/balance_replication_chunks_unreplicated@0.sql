INSERT INTO ba_testsuite_00.balance_replication_chunks
(
    last_accrued_at,
    last_account_id,
    count,
    created,
    updated
)
VALUES
( -- t1i1
    '2019-01-01 11:11:11.000000'::TIMESTAMP,
    22220110000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
),
( -- t1i2
    '2019-01-01 11:11:11.000000'::TIMESTAMP,
    22220120000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
),
( -- t1i3
    '2019-01-01 11:11:11.000000'::TIMESTAMP,
    22220130000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
),
( -- t2i1
    '2019-01-01 12:12:12.000000'::TIMESTAMP,
    22220110000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
),
( -- t2i2
    '2019-01-01 12:12:12.000000'::TIMESTAMP,
    22220120000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
),
( -- t2i3
    '2019-01-01 12:12:12.000000'::TIMESTAMP,
    22220130000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
),
( -- t3i1
    '2019-01-01 13:13:13.000000'::TIMESTAMP,
    22220110000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
),
( -- t3i2
    '2019-01-01 13:13:13.000000'::TIMESTAMP,
    22220120000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
),
( -- t3i3
    '2019-01-01 13:13:13.000000'::TIMESTAMP,
    22220130000,
    0,
    '2019-02-01 00:00:00.000000'::TIMESTAMP,
    '2019-02-01 00:00:00.000000'::TIMESTAMP
);
