INSERT INTO test_schema.fixprefix (id, created_ts)
VALUES
(
    '0',
    '2019-11-20 13:00:00+3'::timestamp with time zone
),
(
    '1',
    '2019-11-20 12:05:00+3'::timestamp with time zone
),
(
    '2',
    '2019-11-20 12:01:00+3'::timestamp with time zone
),
(
    '3',
    '2019-11-20 11:50:00+3'::timestamp with time zone
);
INSERT INTO test_schema.fixprefix_0 (id, created_ts)
VALUES
(
    '4',
    '2019-11-21 11:00:01+3'::timestamp with time zone
);
INSERT INTO test_schema.fixprefix_u12345 (id, created_ts)
VALUES
(
    '5',
    '2019-11-21 11:00:01+3'::timestamp with time zone
),
(
    '6',
    '2019-11-22 04:00:01+3'::timestamp with time zone
);
