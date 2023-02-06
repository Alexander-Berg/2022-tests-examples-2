INSERT INTO test_schema.test_table_comp_pk (id, second_id, created_at_ts, created_at_ts_tz, can_delete, should_not_be_null)
VALUES
(
    '0',
    '0',
    '2017-11-21 10:00:00'::timestamp,
    '2017-11-21 13:00:00+3'::timestamp with time zone,
    true,
    null
);
