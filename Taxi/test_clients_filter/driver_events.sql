INSERT INTO dispatch_airport.driver_events (
  udid,
  event_id,
  event_type,

  driver_id,
  airport_id,
  inserted_ts
) VALUES
(
  'udid16',
  'old_session_id16',
  'entered_on_order_wrong_client',

  'dbid_uuid16',
  'ekb',
  NOW() - INTERVAL '15 minutes'
);
