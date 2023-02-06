INSERT INTO state.uploading_reposition_events(
    event_id,
    event_type,
    driver_id_id,
    occured_at,
    tags,
    uploading,
    uploaded,
    event_created
) VALUES (
    1000,
    ('offer_created')::db.reposition_event_type,
    IdId('uuid3', 'dbid777'),
    '2019-09-01T12:00:00',
    '{"valid_tag", "home"}',
    '2019-09-01T12:00:01',
    TRUE,
    '2019-09-01T12:00:00'
),
(
    1001,
    ('offer_expired')::db.reposition_event_type,
    IdId('uuid3', 'dbid777'),
    '2019-09-01T13:00:00',
    '{"valid_tag", "home"}',
    '2019-09-01T13:00:03',
    FALSE,
    '2019-09-01T12:00:00'
),
(
    1002,
    ('violation')::db.reposition_event_type,
    IdId('uuid3', 'dbid777'),
    '2019-09-01T13:00:00',
    '{"valid_tag", "home"}',
    '2019-09-01T13:00:05',
    FALSE,
    '2019-09-01T12:00:00'
),
(
    1003,
    ('stop')::db.reposition_event_type,
    IdId('uuid3', 'dbid777'),
    '2019-09-01T13:07:00',
    '{"error_tag", "poi"}',
    NULL,
    FALSE,
    '2019-09-01T12:00:00'
);
