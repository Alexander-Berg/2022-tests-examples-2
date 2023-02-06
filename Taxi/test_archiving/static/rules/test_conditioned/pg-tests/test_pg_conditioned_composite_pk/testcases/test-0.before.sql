INSERT INTO test_schema.test_table_comp_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '0',
    '0',
    '2019-11-21 10:00:00'::timestamp,
    '2019-11-21 13:00:00+3'::timestamp with time zone,
    false,
    'www'
),
(
    '1',
    '1',
    '2019-11-21 09:05:00'::timestamp,
    '2019-11-21 12:05:00+3'::timestamp with time zone,
    false,
    'www'
),
(
    '2',
    '2',
    '2019-11-21 09:01:00'::timestamp,
    '2019-11-21 12:01:00+3'::timestamp with time zone,
    true,
    'www'
),
(
    '3',
    '3',
    '2019-11-21 08:50:00'::timestamp,
    '2019-11-21 11:50:00+3'::timestamp with time zone,
    false,
    'www'
),
(
    '4',
    '4',
    '2019-11-21 08:00:01'::timestamp,
    '2019-11-21 11:00:01+3'::timestamp with time zone,
    false,
    'www'
),
(
    '5',
    '5',
    '2019-11-21 08:00:01'::timestamp,
    '2019-11-21 11:00:01+3'::timestamp with time zone,
    false,
    'www'
),
(
    '6',
    '6',
    '2019-11-22 01:00:01'::timestamp,
    '2019-11-22 04:00:01+3'::timestamp with time zone,
    false,
    'www'
),
(
    '7',
    '7',
    '2018-11-21 08:00:00'::timestamp,
    '2019-11-21 11:00:00+3'::timestamp with time zone,
    false,
    'www'
),
(
    '8',
    '8',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    null
),
(
    '9',
    '9',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    'www'
),
(
    '10',
    '10',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    null
),
(
    '11',
    '11',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    false,
    'www'
);
