-- 10 элементов
-- uuid1\2\etc
-- 5 sftp, 5 email
-- 3 created_at_before_2021_06_21
-- 2 created_at_before_2021_06_21_after_2021_06_20
-- 2 updated_at_before_2021_06_22_after_2021_06_20
-- 3 brand_id1, brand_id2
-- 3 place_id1, place_id2

insert into reports
(
    uuid,
    brand_id,
    place_id,
    status,
    type,
    report_type,
    period,

    created_at,
    updated_at
)
values
(
    'uuid1',
    'brand_id1',
    null,
    'in_progress',
    'sftp',
    'test_report_type',
    'daily',

    '2021-06-19 00:00:00',
    '2021-06-21 00:00:00'
),

(
    'uuid2',
    'brand_id1',
    null,
    'new',
    'sftp',
    'test_report_type',
    'daily',

    '2021-06-20 00:00:00',
    '2021-06-20 00:00:00'
),

(
    'uuid3',
    'brand_id2',
    null,
    'in_progress',
    'sftp',
    'test_report_type',
    'daily',

    '2021-06-21 00:00:00',
    '2021-06-22 00:00:00'
),

(
    'uuid4',
    'brand_id3',
    'place_id1',
    'in_progress',
    'sftp',
    'test_report_type',
    'daily',

    '2021-06-22 00:00:00',
    '2021-06-23 00:00:00'
),

(
    'uuid5',
    'brand_id3',
    'place_id1',
    'fail',
    'sftp',
    'test_report_type',
    'daily',

    '2021-06-22 00:00:00',
    '2021-06-24 00:00:00'
),

(
    'uuid6',
    'brand_id3',
    'place_id2',
    'success',
    'email',
    'test_report_type',
    'daily',

    '2021-06-22 00:00:00',
    '2021-06-24 00:00:00'
),

(
    'uuid7',
    'brand_id3',
    'place_id3',
    'success',
    'email',
    'test_report_type',
    'daily',

    '2021-06-22 00:00:00',
    '2021-06-24 00:00:00'
),

(
    'uuid8',
    'brand_id3',
    null,
    'success',
    'email',
    'test_report_type',
    'daily',

    '2021-06-22 00:00:00',
    '2021-06-24 00:00:00'
),

(
    'uuid9',
    'brand_id3',
    null,
    'success',
    'email',
    'test_report_type',
    'daily',

    '2021-06-22 00:00:00',
    '2021-06-24 00:00:00'
),

(
    'uuid10',
    'brand_id3',
    null,
    'success',
    'email',
    'test_report_type',
    'daily',

    '2021-06-22 00:00:00',
    '2021-06-24 00:00:00'
)
;
