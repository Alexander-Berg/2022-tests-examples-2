INSERT INTO state.uploading_reposition_events (
  event_id,
  event_type,
  driver_id_id,
  occured_at,
  tags,
  uploading,
  uploaded,
  event_created
)
VALUES
  (
    1000,
    ('offer_created')::db.reposition_event_type,
    11,
    '2019-09-01T12:00:00',
    NULL,
    '2019-09-01T12:00:00',
    True,
    '2019-09-01T12:00:00'
  ),
  (
    1001,
    ('stop')::db.reposition_event_type,
    11,
    '2019-09-01T11:00:00',
    NULL,
    '2019-09-01T13:00:00',
    False,
    '2019-09-01T11:00:00'
  ),
  (
    1002,
    ('stop')::db.reposition_event_type,
    11,
    '2019-09-01T12:57:30',
    NULL,
    '2019-09-01T13:00:00',
    False,
    '2019-09-01T12:00:00'
  );
