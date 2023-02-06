INSERT INTO dispatch_airport.driver_events (
  udid,
  event_id,
  event_type,

  driver_id,
  airport_id,
  inserted_ts
) VALUES
(
  'udid0',
  'old_session_id0',
  'entered_on_repo',

  'dbid_uuid0',
  'ekb',
  NOW()
),
(
  'udid1',
  'old_session_id1',
  'filtered_by_forbidden_reason',

  'dbid_uuid1',
  'ekb',
  NOW() - INTERVAL '31 minutes'
);
