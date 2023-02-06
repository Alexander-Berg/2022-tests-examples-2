CALL bte.insert_event(
    'event_ref_1',
    '2020-06-30 10:00+00'::timestamptz,
    '2020-06-30 10:00+00'::timestamptz,
    'driver_id_1',
    '1M'::interval,
    '{"1": 2}'
);
CALL bte.insert_event(
    'event_ref_2',
    '2020-06-30 10:01+00'::timestamptz,
    '2020-06-30 10:01+00'::timestamptz,
    'driver_id_1',
    '1M'::interval,
    '{"1": 2}'
);
CALL bte.insert_event(
    'event_ref_3',
    '2020-06-30 10:02+00'::timestamptz,
    '2020-06-30 10:02+00'::timestamptz,
    'driver_id_1',
    '1M'::interval,
    '{"1": 3}'
);
CALL bte.insert_event(
    'event_ref_4',
    '2020-06-30 10:02+00'::timestamptz,
    '2020-06-30 10:02+00'::timestamptz,
    'driver_id_2',
    '1M'::interval,
    '{"1": 3}'
);
CALL bte.insert_event(
    'event_ref_5',
    '2020-06-30 10:02+00'::timestamptz,
    '2020-06-30 10:02+00'::timestamptz,
    'driver_id_3',
    '30S'::interval,
    '{"1": 3}'
);
