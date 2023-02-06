INSERT INTO ba_testsuite_00.balance_at
(
    account_id,
    accrued_at,
    balance,
    journal_id
)
VALUES
(22200010000, '2019-01-10 11:11:11'::TIMESTAMP, 0.00, 300010000),
(22200020000, '2019-01-10 11:11:11'::TIMESTAMP, 1.00, 300010000),
(22200030000, '2019-01-10 11:11:11'::TIMESTAMP, 2.00, 300010000),
(22200040000, '2019-01-10 11:11:11'::TIMESTAMP, 3.00, 300010000),
(22200050000, '2019-01-10 11:11:11'::TIMESTAMP, 4.00, 300010000),
(22200060000, '2019-01-10 11:11:11'::TIMESTAMP, 5.00, 300010000),
(22200070000, '2019-01-10 11:11:11'::TIMESTAMP, 6.00, 300010000), -- chunk0
(22200080000, '2019-01-10 11:11:11'::TIMESTAMP, 7.00, 300010000),
(22200090000, '2019-01-10 11:11:11'::TIMESTAMP, 8.00, 300010000),
(22200100000, '2019-01-10 11:11:11'::TIMESTAMP, 9.00, 300010000),

(22199920009, '2019-01-10 12:12:12'::TIMESTAMP, 0.01, 300020000),
(22199930009, '2019-01-10 12:12:12'::TIMESTAMP, 1.01, 300020000),
(22199940009, '2019-01-10 12:12:12'::TIMESTAMP, 2.01, 300020000),
(22199950009, '2019-01-10 12:12:12'::TIMESTAMP, 3.01, 300020000), -- chunk1
(22199960009, '2019-01-10 12:12:12'::TIMESTAMP, 4.01, 300020000),
(22199970009, '2019-01-10 12:12:12'::TIMESTAMP, 5.01, 300020000), -- chunk2
(22199980009, '2019-01-10 12:12:12'::TIMESTAMP, 6.01, 300020000), -- chunk3
(22199990009, '2019-01-10 12:12:12'::TIMESTAMP, 7.01, 300020000),
(22200000009, '2019-01-10 12:12:12'::TIMESTAMP, 8.01, 300020000),
(22200010009, '2019-01-10 12:12:12'::TIMESTAMP, 9.01, 300020000),

(22200010000, '2019-01-10 13:13:13'::TIMESTAMP, 0.11, 300100000),
(22200020000, '2019-01-10 13:13:13'::TIMESTAMP, 1.11, 300110000), --+ rollup0
(22200030000, '2019-01-10 13:13:13'::TIMESTAMP, 2.11, 300120000),
(22200040000, '2019-01-10 13:13:13'::TIMESTAMP, 3.11, 300130000),
(22200050000, '2019-01-10 13:13:13'::TIMESTAMP, 4.11, 300140000),
(22200060000, '2019-01-10 13:13:13'::TIMESTAMP, 5.11, 300150000),
(22200070000, '2019-01-10 13:13:13'::TIMESTAMP, 6.11, 300160000), --+ rollup1
(22200080000, '2019-01-10 13:13:13'::TIMESTAMP, 7.11, 300170000),
(22200090000, '2019-01-10 13:13:13'::TIMESTAMP, 8.11, 300180000),
(22200100000, '2019-01-10 13:13:13'::TIMESTAMP, 9.11, 300190000),

(22200010000, '2019-01-10 14:14:14'::TIMESTAMP, 0.9999, 300200000),
(22200020000, '2019-01-10 14:14:14'::TIMESTAMP, 1.9999, 300200000), --+
(22200030000, '2019-01-10 14:14:14'::TIMESTAMP, 2.9999, 300200000),
(22200040000, '2019-01-10 14:14:14'::TIMESTAMP, 3.9999, 300200000),
(22200050000, '2019-01-10 14:14:14'::TIMESTAMP, 4.9999, 300200000),
(22200060000, '2019-01-10 14:14:14'::TIMESTAMP, 5.9999, 300200000),
(22200070000, '2019-01-10 14:14:14'::TIMESTAMP, 6.9999, 300200000), --+
(22200080000, '2019-01-10 14:14:14'::TIMESTAMP, 7.9999, 300200000),
(22200090000, '2019-01-10 14:14:14'::TIMESTAMP, 8.9999, 300200000),
(22200100000, '2019-01-10 14:14:14'::TIMESTAMP, 9.9999, 300200000);