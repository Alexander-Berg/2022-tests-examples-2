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
-- chunk #1, size = 2
(
--  FFFFNNNVVVV, F=FILLER,N=REC_NO,V=VSHARD_ID
    22220010000,
    40000,
    1.0000,
    'brand_new/858895/1',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:45:42.811977'
),
(
    22220020000,
    40000,
    1.0000,
    'brand_new/858895/2',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:45:42.811977'
),
-- chunk #2, size = 3
(
    22220030000,
    40000,
    1.0000,
    'brand_new/858895/3',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:45:42.811977'
),
( -- last processed journal entry in rollups
    22220040000,
    40000,
    1.0000,
    'brand_new/858895/4',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:45:42.811977'
),
(
    22220050000,
    40000,
    1.0000,
    'brand_new/858895/5',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:45:42.811977'
),
-- chunk #3, size = 10 (incomplete)
(
    22220060000,
    40000,
    1.0000,
    'brand_new/858895/6',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:45:42.811977'
),
(
    22220070000,
    40000,
    1.0000,
    'brand_new/858895/7',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:48:42.811977'
),
(
    22220080000,
    40000,
    1.0000,
    'brand_new/858895/8',
    '2018-12-20 17:45:42',
    'test',
    '2018-12-20 17:48:42.811977'
),
(
    22220090000,
    40000,
    1.0000,
    'brand_new/858895/9',
    '2018-12-20 17:48:42',
    'test',
    '2018-12-20 17:48:42.811977'
);