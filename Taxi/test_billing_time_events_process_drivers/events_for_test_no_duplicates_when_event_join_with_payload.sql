SELECT bte.create_payloads_partition(
    range_from := '2020-06-30 10:00+00:00',
    range_to := '2020-06-30  11:00+00:00',
    partition_postfix := '2020_070110_2020_070111'
);
SELECT bte.create_payloads_partition(
    range_from := '2020-06-30 11:00+00:00',
    range_to := '2020-06-30 12:00+00:00',
    partition_postfix := '2020_070111_2020_070112'
);

CALL bte.insert_event(
    'event_ref_1',
    '2020-06-30 10:59+00:00'::timestamptz,
    '2020-06-30 10:00+00:00'::timestamptz,
    'dbid_uuid1',
    '1M'::interval,
    '{}'
);
CALL bte.insert_event(
    'event_ref_2',
    '2020-06-30 11:01+00:00'::timestamptz,
    '2020-06-30 10:01+00:00'::timestamptz,
    'dbid_uuid1',
    '1M'::interval,
    '{}'
);
CALL bte.insert_event(
    'event_ref_3',
    '2020-06-30 11:02+00:00'::timestamptz,
    '2020-06-30 10:02+00:00'::timestamptz,
    'dbid_uuid1',
    '2M'::interval,
    '{}'
);
