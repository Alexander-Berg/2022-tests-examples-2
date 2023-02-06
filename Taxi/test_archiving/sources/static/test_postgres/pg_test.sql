INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '0',
    '2019-11-21 10:00:00'::timestamp,
    '2019-11-21 13:00:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '1',
    '2019-11-21 09:05:00'::timestamp,
    '2019-11-21 12:05:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '2',
    '2019-11-21 09:01:00'::timestamp,
    '2019-11-21 12:01:00+3'::timestamp with time zone,
    true,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '3',
    '2019-11-21 08:50:00'::timestamp,
    '2019-11-21 11:50:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '4',
    '2019-11-21 08:00:01'::timestamp,
    '2019-11-21 11:00:01+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '5',
    '2019-11-21 08:00:01'::timestamp,
    '2019-11-21 11:00:01+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '6',
    '2019-11-22 01:00:01'::timestamp,
    '2019-11-22 04:00:01+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '7',
    '2018-11-21 08:00:00'::timestamp,
    '2019-11-21 11:00:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '8',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    null
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '9',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    'www'
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '10',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    null
);
INSERT INTO test_table (id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '11',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '0',
    '00',
    '2019-11-21 10:00:00'::timestamp,
    '2019-11-21 13:00:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '1',
    '11',
    '2019-11-21 09:05:00'::timestamp,
    '2019-11-21 12:05:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '2',
    '22',
    '2019-11-21 09:01:00'::timestamp,
    '2019-11-21 12:01:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '3',
    '33',
    '2019-11-21 08:50:00'::timestamp,
    '2019-11-21 11:50:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '4',
    '44',
    '2019-11-21 08:00:01'::timestamp,
    '2019-11-21 11:00:01+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '5',
    '55',
    '2019-11-21 08:00:01'::timestamp,
    '2019-11-21 11:00:01+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '6',
    '66',
    '2019-11-22 01:00:01'::timestamp,
    '2019-11-22 04:00:01+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '7',
    '77',
    '2018-11-21 08:00:00'::timestamp,
    '2019-11-21 11:00:00+3'::timestamp with time zone,
    false,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '8',
    '88',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    null
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '9',
    '99',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    'www'
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '10',
    '1010',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    true,
    null
);
INSERT INTO test_table_two_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '11',
    '1111',
    '2019-11-21 07:00:00'::timestamp,
    '2019-11-21 10:00:00+3'::timestamp with time zone,
    false,
    'www'
);
