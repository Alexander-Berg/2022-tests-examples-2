INSERT INTO dispatch_airport.driver_events (
    udid,
    event_id,
    event_type,

    driver_id,
    airport_id,
    inserted_ts
) VALUES
(
    'udid1',
    'allowed_1_1',
    'entered_marked_area',

    'dbid_uuid1',
    'ekb',
    '2021-08-19T09:34:00+0000'
),
(
    'udid1',
    'allowed_1_2',
    'entered_marked_area',

    'dbid_uuid1',
    'ekb',
    '2021-08-19T09:35:00+0000'
),
(
    'udid2',
    'forbidden_2_1',
    'entered_marked_area',

    'dbid_uuid2',
    'ekb',
    '2021-08-19T09:34:00+0000'
),
(
    'udid2',
    'forbidden_2_2',
    'entered_marked_area',

    'dbid_uuid2',
    'ekb',
    '2021-08-19T09:35:00+0000'
),
(
    'udid2',
    'forbidden_2_3',
    'entered_marked_area',

    'dbid_uuid2',
    'ekb',
    '2021-08-19T09:36:00+0000'
);


