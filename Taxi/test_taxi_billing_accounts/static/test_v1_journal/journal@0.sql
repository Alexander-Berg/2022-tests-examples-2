INSERT INTO ba_testsuite_00.journal
(
    id,
    account_id,
    amount,
    doc_ref,
    event_at,
    reason,
    created
)
VALUES
(
    34720250000,
    40000,
    1.0000,
    'brand_new/858895/1',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:45:42.811977'
),
(
    34720260000,
    40000,
    2.0000,
    'brand_new/858895/2',
    '2018-12-20 17:45:43',
    'test',
    '2018-12-20 17:45:43.811977'
),
(
    34720270000,
    40000,
    3.0000,
    'brand_new/858895/3',
    '2018-12-20 17:45:43',
    'test',
    '2018-12-20 17:45:43.811977'
),
(
    34720280000,
    41000,
    300.0000,
    'brand_new/858895/3',
    '2018-12-20 17:45:43',
    'test',
    '2018-12-20 17:45:43.811977'
)
;

-- Entries with filled details
INSERT INTO ba_testsuite_00.journal
(
    id,
    account_id,
    amount,
    doc_ref,
    event_at,
    reason,
    created,
    details
)
VALUES
(
    34720300000,
    40000,
    1.0000,
    'brand_new/858895/30',
    '2018-12-20 18:45:42',
    'test',
    '2018-12-20 18:45:42.811977',
    '{"alias_id": "some_alias_id"}'::jsonb
),
(
    34720800000,
    41000,
    9.0000,
    'brand_new/858895/31',
    '2018-11-19 18:45:42',
    'test',
    '2018-12-20 18:45:42.811977',
    '{"alias_id": "some_alias_id"}'::jsonb
)
;

-- Reset sequence to the last entry
SELECT setval('ba_testsuite_00.journal_id_seq', 3472100);
